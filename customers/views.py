from django.shortcuts import render, redirect
from .models import Customer
from .forms import CustomerForm

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "customer_list.html", {"customers": customers})

def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()

    return render(request, "add_customer.html", {"form": form})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import Customer


def delete_customer(request, id):

    customer = get_object_or_404(
        Customer,
        id=id
    )

    if request.method == "POST":

        customer.delete()

        messages.success(
            request,
            "Customer successfully deleted."
        )

        return redirect("customer_list")

    return redirect("customer_list")
