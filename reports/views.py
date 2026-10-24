from django.shortcuts import render
from orders.models import Order
from purchases.models import Purchase


def reports(request):

    # =========================
    # SALES
    # =========================

    orders = Order.objects.all().order_by("-created_at")


    # =========================
    # PURCHASES
    # =========================

    purchases = Purchase.objects.all().order_by("-date")


    # =========================
    # TOTALS
    # =========================

    total_sales = sum(
        order.total_price or 0
        for order in orders
    )

    total_purchased = sum(
        purchase.quantity or 0
        for purchase in purchases
    )

    total_purchase_amount = sum(
        (purchase.purchase_price or 0) * purchase.quantity
        for purchase in purchases
    )

    context = {

        "orders": orders,

        "purchases": purchases,

        "total_sales": total_sales,

        "total_purchased": total_purchased,

        "total_purchase_amount": total_purchase_amount,

    }


    return render(
        request,
        "reports/reports.html",
        context
    )