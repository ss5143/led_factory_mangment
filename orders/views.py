from decimal import Decimal, InvalidOperation


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from products.models import Product
from customers.models import Customer

from .models import Order, OrderItem
from .forms import OrderForm


# =========================================================
# ADD ORDER
# =========================================================

@login_required(login_url="login")
@transaction.atomic

def add_order(request):
    """
    Create a new order.

    Each selected product has its own:
    - quantity
    - sale price

    Example:
        DC Light 12W  -> Qty 10 -> Sale Price 150
        LED Bulb 12W  -> Qty 5  -> Sale Price 100
    """

    products = Product.objects.all().order_by("category", "watt")

    if request.method == "POST":

        # =====================================================
        # CUSTOMER
        # =====================================================

        customer_name = request.POST.get(
            "customer_name",
            "Walk-in Customer"
        ).strip()

        if not customer_name:
            customer_name = "Walk-in Customer"


        # =====================================================
        # CREATE ORDER
        # =====================================================

        order = Order.objects.create(
            customer_name=customer_name,
            total_price=Decimal("0.00"),
            status="Pending",
        )


        grand_total = Decimal("0.00")
        selected_products = 0


        # =====================================================
        # PROCESS PRODUCTS
        # =====================================================

        for product in products:

            quantity_raw = request.POST.get(
                f"quantity_{product.id}",
                "0"
            )

            sale_price_raw = request.POST.get(
                f"sale_price_{product.id}",
                "0"
            )


            # -------------------------------------------------
            # QUANTITY
            # -------------------------------------------------

            try:
                quantity = int(quantity_raw or 0)
            except (ValueError, TypeError):
                quantity = 0


            # Product not selected
            if quantity <= 0:
                continue


            # -------------------------------------------------
            # CHECK STOCK
            # -------------------------------------------------

            if quantity > product.stock:

                order.delete()

                messages.error(
                    request,
                    f"{product.category} - "
                    f"{product.watt}W: "
                    f"Only {product.stock} pcs available "
                    f"in stock."
                )

                return render(
                    request,
                    "add_order.html",
                    {
                        "form": OrderForm(
                            initial={
                                "customer_name": customer_name
                            }
                        ),
                        "products": products,
                    }
                )


            # -------------------------------------------------
            # SALE PRICE
            # -------------------------------------------------

            try:
                sale_price = Decimal(
                    sale_price_raw or "0"
                )
            except (InvalidOperation, ValueError, TypeError):
                sale_price = Decimal("0.00")


            if sale_price < 0:

                order.delete()

                messages.error(
                    request,
                    f"{product.category} - "
                    f"{product.watt}W: "
                    f"Sale price cannot be negative."
                )

                return render(
                    request,
                    "add_order.html",
                    {
                        "form": OrderForm(
                            initial={
                                "customer_name": customer_name
                            }
                        ),
                        "products": products,
                    }
                )


            # -------------------------------------------------
            # PURCHASE PRICE
            # -------------------------------------------------

            purchase_price = (
                product.purchase_price
                or Decimal("0.00")
            )


            # -------------------------------------------------
            # ITEM TOTAL
            # -------------------------------------------------

            item_total = (
                sale_price * quantity
            )


            # -------------------------------------------------
            # ITEM PROFIT
            # -------------------------------------------------

            item_profit = (
                (sale_price - purchase_price)
                * quantity
            )


            # -------------------------------------------------
            # CREATE ORDER ITEM
            # -------------------------------------------------

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=sale_price,
                purchase_price=purchase_price,
                total_price=item_total,
                profit=item_profit,
            )


            # -------------------------------------------------
            # REDUCE STOCK
            # -------------------------------------------------

            product.stock -= quantity
            product.save(
                update_fields=["stock"]
            )


            # -------------------------------------------------
            # ORDER TOTALS
            # -------------------------------------------------

            grand_total += item_total
            grand_profit += item_profit

            selected_products += 1


        # =====================================================
        # NO PRODUCT SELECTED
        # =====================================================

        if selected_products == 0:

            order.delete()

            messages.error(
                request,
                "Please select at least one product."
            )

            return render(
                request,
                "add_order.html",
                {
                    "form": OrderForm(
                        initial={
                            "customer_name": customer_name
                        }
                    ),
                    "products": products,
                }
            )


        # =====================================================
        # SAVE ORDER TOTALS
        # =====================================================

        order.total_price = grand_total

        order.save(
            update_fields=[
                "total_price",
            ]
        )


        # =====================================================
        # SUCCESS
        # =====================================================

        messages.success(
            request,
            f"Order #{order.id} created successfully."
        )

        return redirect(
            "orders:orders"
        )


    # =========================================================
    # GET
    # =========================================================

    form = OrderForm()

    return render(
        request,
        "add_order.html",
        {
            "form": form,
            "products": products,
        }
    )



# =========================================================
# ORDERS LIST
# =========================================================

@login_required(login_url="login")
def orders(request):

    order_list = (
        Order.objects
        .prefetch_related("items__product")
        .order_by("-id")
    )

    return render(
        request,
        "order_list.html",
        {
            "orders": order_list,
        }
    )


# =========================================================
# ORDER DETAIL
# =========================================================

@login_required(login_url="login")
def order_detail(request, id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__product"
        ),
        id=id
    )

    return render(
        request,
        "order_list.html",
        {
            "orders": [order],
        }
    )


# =========================================================
# EDIT ORDER
# ADD PRODUCT + CHANGE QTY + DELETE
# STOCK + PROFIT RECALCULATION
# =========================================================

@login_required(login_url="login")
@transaction.atomic
def edit_order(request, id):

    order = get_object_or_404(
        Order,
        id=id
    )

    # =====================================================
    # DELETE ITEM
    # =====================================================

    if (
        request.method == "POST"
        and request.POST.get("delete_item")
    ):

        item_id = request.POST.get("delete_item")

        item = get_object_or_404(
            OrderItem,
            id=item_id,
            order=order
        )

        product = item.product

        # Return stock
        product.stock += item.quantity

        product.save(
            update_fields=["stock"]
        )

        product_name = (
            f"{product.category} - {product.watt}W"
        )

        item.delete()

        recalculate_order(order)

        messages.success(
            request,
            f"{product_name} deleted from Order #{order.id}."
        )

        return redirect(
            "orders:edit_order",
            id=order.id
        )

    # =====================================================
    # ADD NEW PRODUCT
    # =====================================================

    if (
        request.method == "POST"
        and request.POST.get("add_product")
    ):

        product_id = request.POST.get("product_id")
        quantity_text = request.POST.get(
            "quantity",
            "1"
        ).strip()

        sale_price_text = request.POST.get(
            "sale_price",
            ""
        ).strip()

        if not product_id:
            messages.error(
                request,
                "Please select a product."
            )
            return redirect(
                "orders:edit_order",
                id=order.id
            )

        try:
            quantity = int(quantity_text)
        except (ValueError, TypeError):
            quantity = 0

        if quantity <= 0:
            messages.error(
                request,
                "Quantity must be greater than 0."
            )
            return redirect(
                "orders:edit_order",
                id=order.id
            )

        product = get_object_or_404(
            Product,
            id=product_id
        )

        if quantity > product.stock:
            messages.error(
                request,
                f"{product.category} - "
                f"{product.watt}W: Only "
                f"{product.stock} pcs available."
            )
            return redirect(
                "orders:edit_order",
                id=order.id
            )

        # Use entered sale price.
        # If blank, use the product's default sale price.
        if sale_price_text == "":
            sale_price = (
                product.sale_price
                or Decimal("0.00")
            )
        else:
            try:
                sale_price = Decimal(
                    sale_price_text
                )
            except (
                InvalidOperation,
                ValueError,
                TypeError
            ):
                messages.error(
                    request,
                    "Please enter a valid Sale Price."
                )
                return redirect(
                    "orders:edit_order",
                    id=order.id
                )

        if sale_price < 0:
            messages.error(
                request,
                "Sale Price cannot be negative."
            )
            return redirect(
                "orders:edit_order",
                id=order.id
            )

        purchase_price = (
            product.purchase_price
            or Decimal("0.00")
        )

        # If product already exists in this order,
        # add quantity but keep its existing sale price.
        item = (
            OrderItem.objects
            .filter(
                order=order,
                product=product
            )
            .first()
        )

        if item:
            item.quantity += quantity
            # Keep the existing per-product sale price.
            # The entered price is used only for a new product.
            item.purchase_price = purchase_price
            item.total_price = (
                item.unit_price * item.quantity
            )
            item.profit = (
                item.unit_price - purchase_price
            ) * item.quantity
            item.save()

        else:
            item_total = (
                sale_price * quantity
            )

            item_profit = (
                sale_price - purchase_price
            ) * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=sale_price,
                purchase_price=purchase_price,
                total_price=item_total,
                profit=item_profit,
            )

        # Reduce stock.
        product.stock -= quantity
        product.save(
            update_fields=["stock"]
        )

        # Recalculate order total.
        recalculate_order(order)

        messages.success(
            request,
            f"{product.category} - "
            f"{product.watt}W added to "
            f"Order #{order.id}."
        )

        return redirect(
            "orders:edit_order",
            id=order.id
        )

    # =====================================================
    # UPDATE QUANTITIES + PER-PRODUCT SALE PRICE
    # =====================================================

    if (
        request.method == "POST"
        and request.POST.get("update_order")
    ):

        items = list(
            order.items
            .select_related("product")
            .all()
        )

        errors = []
        changes = []

        # Validate everything first.
        for item in items:

            product = item.product

            quantity_text = request.POST.get(
                f"quantity_{item.id}",
                str(item.quantity)
            )

            sale_price_text = request.POST.get(
                f"sale_price_{item.id}",
                str(item.unit_price or "0")
            ).strip()

            try:
                new_quantity = int(quantity_text)
            except (ValueError, TypeError):
                errors.append(
                    f"{product.category} - {product.watt}W: "
                    f"Invalid quantity."
                )
                continue

            try:
                new_sale_price = Decimal(
                    sale_price_text or "0"
                )
            except (InvalidOperation, ValueError, TypeError):
                errors.append(
                    f"{product.category} - {product.watt}W: "
                    f"Invalid sale price."
                )
                continue

            if new_quantity < 0:
                errors.append(
                    f"{product.category} - {product.watt}W: "
                    f"Quantity cannot be negative."
                )
                continue

            if new_sale_price < 0:
                errors.append(
                    f"{product.category} - {product.watt}W: "
                    f"Sale price cannot be negative."
                )
                continue

            difference = new_quantity - item.quantity

            if difference > 0 and difference > product.stock:
                errors.append(
                    f"{product.category} - {product.watt}W: "
                    f"Only {product.stock} pcs available "
                    f"for additional quantity."
                )
                continue

            changes.append({
                "item": item,
                "new_quantity": new_quantity,
                "new_sale_price": new_sale_price,
                "difference": difference,
            })

        if errors:

            for error in errors:
                messages.error(request, error)

        else:

            # Apply changes only after all validation succeeds.
            for change in changes:

                item = change["item"]
                new_quantity = change["new_quantity"]
                new_sale_price = change["new_sale_price"]
                difference = change["difference"]

                product = item.product

                if difference > 0:
                    product.stock -= difference

                elif difference < 0:
                    product.stock += abs(difference)

                product.save(
                    update_fields=["stock"]
                )

                if new_quantity == 0:
                    item.delete()
                    continue

                item.quantity = new_quantity
                item.unit_price = new_sale_price
                item.purchase_price = (
                    product.purchase_price
                    or Decimal("0.00")
                )
                item.total_price = (
                    new_sale_price * new_quantity
                )
                item.profit = (
                    new_sale_price - item.purchase_price
                ) * new_quantity

                item.save()

            recalculate_order(order)

            messages.success(
                request,
                f"Order #{order.id} updated successfully."
            )

        return redirect(
            "orders:edit_order",
            id=order.id
        )

    # =====================================================
    # GET
    # =====================================================

    items = (
        order.items
        .select_related("product")
        .all()
    )

    available_products = (
        Product.objects
        .all()
        .order_by(
            "category",
            "watt"
        )
    )

    return render(
        request,
        "edit_order.html",
        {
            "order": order,
            "items": items,
            "available_products": available_products,
        }
    )


# =========================================================
# RECALCULATE ORDER
# =========================================================


def recalculate_order(order):

    items = (
        order.items
        .select_related("product")
        .all()
    )

    grand_total = Decimal("0.00")
    # =====================================================
    # RECALCULATE EACH PRODUCT
    # =====================================================

    for item in items:

        product = item.product

        # Product ka actual purchase price
        purchase_price = (
            product.purchase_price
            or Decimal("0.00")
        )

        # IMPORTANT:
        # Har product ka apna saved sale price
        sale_price = (
            item.unit_price
            or Decimal("0.00")
        )

        # Purchase price update
        item.purchase_price = purchase_price

        # Total
        item.total_price = (
            sale_price * item.quantity
        )

        # Profit
        item.profit = (
            (sale_price - purchase_price)
            * item.quantity
        )

        item.save(
            update_fields=[
                "unit_price",
                "purchase_price",
                "total_price",
                "profit",
            ]
        )

        grand_total += item.total_price
    # =====================================================
    # UPDATE ORDER
    # =====================================================

    order.total_price = grand_total
    order.save(
        update_fields=[
            "total_price",
        ]
    )


# =========================================================
# MARK PAID
# =========================================================

@login_required(login_url="login")
@transaction.atomic
def mark_paid(request, id):

    order = get_object_or_404(
        Order,
        id=id
    )

    order.status = "Paid"

    order.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        f"Order #{order.id} marked as Paid."
    )

    return redirect(
        "orders:orders"
    )


# =========================================================
# INVOICE
# =========================================================

@login_required(login_url="login")
def invoice(request, id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__product"
        ),
        id=id
    )

    return render(
        request,
        "invoice.html",
        {
            "order": order,
        }
    )


# =========================================================
# INVOICE PDF
# =========================================================

@login_required(login_url="login")
def invoice_pdf(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__product"
        ),
        id=order_id
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="invoice-{order.id}.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=A4
    )

    width, height = A4

    # =====================================================
    # HEADER
    # =====================================================

    pdf.setFillColor(
        colors.HexColor("#166534")
    )

    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawString(
        50,
        height - 60,
        "LED FACTORY"
    )

    pdf.setFillColor(colors.black)

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        50,
        height - 80,
        "Premium LED Lighting Solutions"
    )

    pdf.drawString(
        50,
        height - 95,
        "Main Market, Pakistan"
    )

    pdf.drawString(
        50,
        height - 110,
        "Phone: +92 3465811678"
    )

    # =====================================================
    # INVOICE
    # =====================================================

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawRightString(
        width - 50,
        height - 60,
        "INVOICE"
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawRightString(
        width - 50,
        height - 80,
        f"#INV-{order.id}"
    )

    if order.created_at:

        pdf.drawRightString(
            width - 50,
            height - 95,
            order.created_at.strftime("%d %b %Y")
        )

        pdf.drawRightString(
            width - 50,
            height - 110,
            order.created_at.strftime("%I:%M %p")
        )

    # =====================================================
    # CUSTOMER
    # =====================================================

    y = height - 160

    pdf.setFillColor(
        colors.HexColor("#166534")
    )

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        50,
        y,
        "BILL TO"
    )

    pdf.setFillColor(colors.black)

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        50,
        y - 22,
        order.customer_name or "Walk-in Customer"
    )

    # =====================================================
    # STATUS
    # =====================================================

    pdf.setFillColor(
        colors.HexColor("#166534")
    )

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawRightString(
        width - 50,
        y,
        str(order.status).upper()
    )

    # =====================================================
    # TABLE HEADER
    # =====================================================

    y -= 75

    pdf.setFillColor(
        colors.HexColor("#166534")
    )

    pdf.rect(
        45,
        y - 8,
        width - 90,
        25,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(colors.white)

    pdf.setFont(
        "Helvetica-Bold",
        9
    )

    pdf.drawString(55, y, "#")
    pdf.drawString(80, y, "PRODUCT")
    pdf.drawString(280, y, "WATT")
    pdf.drawString(345, y, "QTY")
    pdf.drawString(395, y, "UNIT PRICE")
    pdf.drawString(500, y, "TOTAL")

    # =====================================================
    # ITEMS
    # =====================================================

    y -= 30

    pdf.setFillColor(colors.black)

    pdf.setFont(
        "Helvetica",
        9
    )

    items = (
        order.items
        .select_related("product")
        .all()
    )

    for index, item in enumerate(
        items,
        start=1
    ):

        product = item.product

        product_name = (
            f"{product.category} - "
            f"{product.watt}W"
        )

        quantity = item.quantity

        unit_price = (
            item.unit_price
            or Decimal("0.00")
        )

        item_total = (
            item.total_price
            or (unit_price * quantity)
        )

        pdf.drawString(
            55,
            y,
            str(index)
        )

        pdf.drawString(
            80,
            y,
            product_name[:30]
        )

        pdf.drawString(
            280,
            y,
            str(product.watt)
        )

        pdf.drawString(
            345,
            y,
            str(quantity)
        )

        pdf.drawString(
            395,
            y,
            f"Rs. {unit_price:.2f}"
        )

        pdf.drawString(
            500,
            y,
            f"Rs. {item_total:.2f}"
        )

        pdf.setStrokeColor(
            colors.lightgrey
        )

        pdf.line(
            50,
            y - 8,
            width - 50,
            y - 8
        )

        y -= 28

        # =================================================
        # NEW PAGE
        # =================================================

        if y < 100:

            pdf.showPage()

            y = height - 60

            pdf.setFillColor(
                colors.black
            )

            pdf.setFont(
                "Helvetica",
                9
            )

    # =====================================================
    # TOTAL
    # =====================================================

    y -= 20

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        400,
        y,
        "GRAND TOTAL:"
    )

    pdf.drawRightString(
        width - 50,
        y,
        f"Rs. {order.total_price:.2f}"
    )

    # =====================================================
    # FOOTER
    # =====================================================

    pdf.setFillColor(
        colors.HexColor("#166534")
    )

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        50,
        65,
        "Thank You!"
    )

    pdf.setFillColor(colors.grey)

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        50,
        48,
        "Thank you for choosing LED Factory."
    )

    pdf.drawString(
        50,
        35,
        "We appreciate your business."
    )

    pdf.save()

    return response


# =========================================================
# DELETE ORDER
# =========================================================

@login_required(login_url="login")
@transaction.atomic
def delete_order(request, id):

    order = get_object_or_404(
        Order.objects.select_for_update(),
        id=id
    )

    # Only POST can delete
    if request.method == "POST":

        items = (
            order.items
            .select_related("product")
            .all()
        )

        # =================================================
        # RETURN STOCK
        # =================================================

        for item in items:

            product = (
                Product.objects
                .select_for_update()
                .get(
                    id=item.product.id
                )
            )

            product.stock += item.quantity

            product.save(
                update_fields=["stock"]
            )

        order_number = order.id

        # =================================================
        # DELETE ORDER
        # =================================================

        order.delete()

        messages.success(
            request,
            f"Order #{order_number} deleted successfully. "
            f"Stock has been restored."
        )

    return redirect(
        "orders:orders"
    )
