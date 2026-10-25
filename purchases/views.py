from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import PurchaseForm


@login_required(login_url="login")
def add_purchase(request):
    if request.method == "POST":
        form = PurchaseForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                purchase = form.save(commit=False)
                product = purchase.product

                if product.user_id != request.user.id:
                    form.add_error("product", "Please select your own product.")
                else:
                    purchase.user = request.user
                    product.stock += purchase.quantity
                    product.save(update_fields=["stock"])
                    purchase.save()
                    return redirect("home")
    else:
        form = PurchaseForm()

    return render(request, "add_purchase.html", {"form": form})
