
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import SupplierForm
from .models import Supplier


@login_required(login_url="login")
def supplier_list(request):
    suppliers = Supplier.objects.filter(user=request.user)
    return render(request, "supplier_list.html", {"suppliers": suppliers})


@login_required(login_url="login")
def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.user = request.user
            supplier.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm()

    return render(request, "add_supplier.html", {"form": form})


@login_required(login_url="login")
def delete_supplier(request, id):
    supplier = get_object_or_404(
        Supplier,
        id=id,
        user=request.user,
    )

    if request.method == "POST":
        supplier.delete()
        messages.success(request, "Supplier deleted successfully.")

    return redirect("supplier_list")
