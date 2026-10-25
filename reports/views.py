from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order
from purchases.models import Purchase


@login_required(login_url="login")
def reports(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    purchases = Purchase.objects.filter(user=request.user).order_by("-date")

    total_sales = sum(order.total_price or 0 for order in orders)
    total_purchased = sum(purchase.quantity or 0 for purchase in purchases)
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

    return render(request, "reports/reports.html", context)
