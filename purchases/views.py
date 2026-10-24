from django.shortcuts import render, redirect
from .forms import PurchaseForm

def add_purchase(request):
    if request.method == "POST":
        form = PurchaseForm(request.POST)

        if form.is_valid():
            purchase = form.save(commit=False)

            product = purchase.product
            product.stock += purchase.quantity
            product.save()

            purchase.save()

            return redirect("home")

    else:
        form = PurchaseForm()

    return render(request, "add_purchase.html", {"form": form})
