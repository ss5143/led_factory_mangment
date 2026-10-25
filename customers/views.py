from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Customer
from .forms import CustomerForm


@login_required(login_url="login")
def customer_list(request):
    customers = Customer.objects.filter(user=request.user)
    return render(request, "customer_list.html", {"customers": customers})


@login_required(login_url="login")
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()

    return render(request, "add_customer.html", {"form": form})


@login_required(login_url="login")
def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id, user=request.user)

    if request.method == "POST":
        customer.delete()
        messages.success(request, "Customer successfully deleted.")

    return redirect("customer_list")
