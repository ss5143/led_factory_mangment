from django.shortcuts import render, redirect
from .forms import SupplierForm
from .models import Supplier

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "supplier_list.html", {"suppliers": suppliers})

def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm()

    return render(request, "add_supplier.html", {"form": form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Supplier


def delete_supplier(request, id):

    supplier = get_object_or_404(
        Supplier,
        id=id
    )

    if request.method == "POST":

        supplier.delete()

        messages.success(
            request,
            "Supplier deleted successfully."
        )

    return redirect("supplier_list")