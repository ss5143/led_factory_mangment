from decimal import Decimal
from django.db import models

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.core.paginator import Paginator
from django.db.models import (
    Sum,
    F,
    DecimalField,
    ExpressionWrapper,
)
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone

from openpyxl import Workbook

from orders.models import Order, OrderItem
from purchases.models import Purchase

from .models import Product
from .forms import ProductForm


# =========================================================
# DASHBOARD
# =========================================================

@login_required(login_url="login")
def home(request):

    # =====================================================
    # PRODUCTS
    # =====================================================

    search = request.GET.get("search", "").strip()


    if search:
      product_list = (
         Product.objects
          .filter(user=request.user)
           .filter(
              models.Q(category__icontains=search)
             | models.Q(watt__icontains=search)
         )
        .order_by("id")
    )

    else:
        product_list = (
            Product.objects
            .filter(user=request.user)
            .order_by("id")
        )

    paginator = Paginator(product_list, 10)

    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    # =====================================================
    # TOTAL PRODUCTS
    # =====================================================

    total_products = Product.objects.filter(user=request.user).count()

    # =====================================================
    # TOTAL STOCK
    # =====================================================

    total_stock = (
        Product.objects.filter(user=request.user).aggregate(
            total=Sum("stock")
        )["total"]
        or 0
    )

    # =====================================================
    # TOTAL SOLD
    # =====================================================

    total_sold = (
        OrderItem.objects.filter(order__user=request.user).aggregate(
            total=Sum("quantity")
        )["total"]
        or 0
    )

    # =====================================================
    # TOTAL SALES
    # =====================================================

    sales_amount = (
        Order.objects.filter(user=request.user).aggregate(
            total=Sum("total_price")
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # TOTAL PURCHASED QUANTITY
    # =====================================================

    total_purchased = (
        Purchase.objects.filter(user=request.user).aggregate(
            total=Sum("quantity")
        )["total"]
        or 0
    )

    # =====================================================
    # TOTAL PURCHASE AMOUNT
    #
    # purchase_price × quantity
    # =====================================================

    purchase_amount = (
        Purchase.objects.filter(user=request.user).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("purchase_price") * F("quantity"),
                    output_field=DecimalField(
                        max_digits=14,
                        decimal_places=2,
                    ),
                )
            )
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # TOTAL PROFIT
    #
    # Profit already calculated in Order model
    # =====================================================

    profit = OrderItem.objects.filter(order__user=request.user).aggregate(
        total=Sum("profit")
    )["total"] or 0

    # =====================================================
    # LOW STOCK
    # =====================================================

    low_stock = (
        Product.objects
        .filter(user=request.user, stock__lt=10)
        .order_by("stock", "id")
    )

    # =====================================================
    # RECENT PURCHASES
    # =====================================================

    recent_purchases = (
    Purchase.objects
    .filter(user=request.user)
    .select_related("product")
    .order_by("-id")[:5]
    )
    # =====================================================
    # RECENT ORDERS
    # =====================================================

    recent_orders = (
    Order.objects
    .filter(user=request.user)
    .prefetch_related("items__product")
    .order_by("-id")[:5]
    )
    # =====================================================
    # MONTHLY SALES
    # =====================================================

    monthly_sales = (
    Order.objects
    .filter(user=request.user)
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(total=Sum("total_price"))
    .order_by("month")
    )
    chart_labels = [
        sale["month"].strftime("%b %Y")
        for sale in monthly_sales
        if sale["month"]
    ]

    chart_data = [
        float(sale["total"] or 0)
        for sale in monthly_sales
    ]

    sales_chart_labels = ["Sales"]
    sales_chart_data = [float(total_sold)]

    # =====================================================
    # TODAY
    # =====================================================

    today = timezone.localdate()

    today_orders = Order.objects.filter(
     user=request.user,
     created_at__date=today,
    )

    today_order_items = (
        OrderItem.objects
        .filter(order__user=request.user,order__created_at__date=today)
    )

    today_purchases = Purchase.objects.filter(
     user=request.user,
     date=today,
    )
    # =====================================================
    # TODAY SOLD
    # =====================================================

    today_sold = (
        today_order_items.aggregate(
            total=Sum("quantity")
        )["total"]
        or 0
    )

    # =====================================================
    # TODAY SALES
    # =====================================================

    today_sales = (
        today_orders.aggregate(
            total=Sum("total_price")
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # TODAY PURCHASED
    # =====================================================

    today_purchased = (
        today_purchases.aggregate(
            total=Sum("quantity")
        )["total"]
        or 0
    )

    # =====================================================
    # TODAY PURCHASE AMOUNT
    #
    # purchase_price × quantity
    # =====================================================

    today_purchase_amount = (
        today_purchases.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("purchase_price") * F("quantity"),
                    output_field=DecimalField(
                        max_digits=14,
                        decimal_places=2,
                    ),
                )
            )
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # TODAY PROFIT
    # =====================================================

    today_profit = (
        today_order_items.aggregate(
            total=Sum("profit")
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # TODAY ORDERS COUNT
    # =====================================================

    today_orders_count = today_orders.count()

    # =====================================================
    # PRODUCT WISE BUSINESS
    # =====================================================

    product_sales = []

    all_products = (
        Product.objects.filter(
            user=request.user
        )
        .order_by("id")
    )

    for product in all_products:

        # -------------------------------------------------
        # SOLD
        # -------------------------------------------------

        sold = (
            OrderItem.objects
            .filter(product=product,order__user=request.user,)
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        # -------------------------------------------------
        # PURCHASED
        # -------------------------------------------------

        purchased = (
            Purchase.objects
            .filter(product=product,user=request.user,)
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        # -------------------------------------------------
        # SALES
        # -------------------------------------------------

        sales = (
            OrderItem.objects
            .filter(product=product, order__user=request.user,)
            .aggregate(
                total=Sum("total_price")
            )["total"]
            or Decimal("0.00")
        )

        # -------------------------------------------------
        # PROFIT
        # -------------------------------------------------

        product_profit = (
            OrderItem.objects
            .filter(product=product)
            .aggregate(
                total=Sum("profit")
            )["total"]
            or Decimal("0.00")
        )

        product_sales.append({
            "product": product,
            "sold": sold,
            "purchased": purchased,
            "stock": product.stock,
            "sales": sales,
            "profit": product_profit,
        })

    # =====================================================
    # TODAY PRODUCT WISE SALES
    # =====================================================

    today_product_sales = []

    for product in all_products:

        orders_today = (
            OrderItem.objects
            .filter(
                product=product,
                order__user=request.user,
                order__created_at__date=today,
            )
        )

        # -------------------------------------------------
        # SOLD
        # -------------------------------------------------

        sold = (
            orders_today.aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        # -------------------------------------------------
        # SALES
        # -------------------------------------------------

        sales = (
            orders_today.aggregate(
                total=Sum("total_price")
            )["total"]
            or Decimal("0.00")
        )

        # -------------------------------------------------
        # PROFIT
        # -------------------------------------------------

        product_profit = (
            orders_today.aggregate(
                total=Sum("profit")
            )["total"]
            or Decimal("0.00")
        )

        today_product_sales.append({
            "product": product,
            "sold": sold,
            "sales": sales,
            "profit": product_profit,
        })

    # =====================================================
    # DASHBOARD
    # =====================================================

    return render(
        request,
        "home.html",
        {
            "products": products,

            "total_products": total_products,

            "total_stock": total_stock,

            "total_sold": total_sold,

            "total_purchased": total_purchased,

            "sales_amount": sales_amount,

            "purchase_amount": purchase_amount,

            "low_stock": low_stock,

            "recent_purchases": recent_purchases,

            "recent_orders": recent_orders,

            "sales_chart_labels": sales_chart_labels,

            "sales_chart_data": sales_chart_data,

            "chart_labels": chart_labels,

            "chart_data": chart_data,

            # =================================================
            # TODAY
            # =================================================

            "today_sold": today_sold,

            "today_sales": today_sales,

            "today_purchased": today_purchased,

            "today_purchase_amount": today_purchase_amount,

            "today_profit": today_profit,

            "today_orders_count": today_orders_count,

            # =================================================
            # PRODUCT WISE
            # =================================================

            "product_sales": product_sales,

            "today_product_sales": today_product_sales,
        }
    )


# =========================================================
# ADD PRODUCT
# =========================================================

@login_required(login_url="login")
def add_product(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            product = form.save(commit=False)
            product.user = request.user
            product.save()

            return redirect("home")

    else:

        form = ProductForm()

    return render(
        request,
        "add_product.html",
        {
            "form": form,
        }
    )


# =========================================================
# EDIT PRODUCT
# =========================================================

@login_required(login_url="login")
def edit_product(request, id):

    product = get_object_or_404(
        Product,
        id=id,
        user=request.user,
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )

        if form.is_valid():

            form.save()

            return redirect("home")

    else:

        form = ProductForm(
            instance=product,
        )

    return render(
        request,
        "add_product.html",
        {
            "form": form,
            "product": product,
        }
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@login_required(login_url="login")
def delete_product(request, id):

    product = get_object_or_404(
        Product,
        id=id,
        user=request.user,
    )

    product.delete()

    return redirect("home")


# =========================================================
# PRODUCT DETAIL
# =========================================================

@login_required(login_url="login")
def product_detail(request, id):

    product = get_object_or_404(
        Product,
        id=id,
        user=request.user,
    )

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
        }
    )


# =========================================================
# EXPORT PRODUCTS EXCEL
# =========================================================

@login_required(login_url="login")
def export_products_excel(request):

    wb = Workbook()

    ws = wb.active

    ws.title = "Products"

    ws.append([
        "Product",
        "Category",
        "Brand",
        "Watt",
        "Sale Price",
        "Purchase Price",
        "Stock",
    ])

    products = (
        Product.objects
        .filter(user=request.user)
        .order_by("id")
    )

    for product in products:

        ws.append([
            f"{product.category} - {product.watt}W",
            product.category,
            f"{product.category} - {product.watt}W",
            product.watt,
            product.sale_price,
            product.purchase_price,
            product.stock,
        ])

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="Products.xlsx"'
    )

    wb.save(response)

    return response
