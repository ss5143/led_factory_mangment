
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Company


@login_required
def edit_company(request):
    company, created = Company.objects.get_or_create(
        user=request.user,
        defaults={
            "name": "",
            "address": "",
            "phone": "",
            "email": "",
        },
    )

    if request.method == "POST":
        company.name = request.POST.get("name", "").strip()
        company.address = request.POST.get("address", "").strip()
        company.phone = request.POST.get("phone", "").strip()
        company.email = request.POST.get("email", "").strip()
        company.website = request.POST.get("website", "").strip()

        if request.FILES.get("logo"):
            company.logo = request.FILES["logo"]

        company.save()
        messages.success(
            request,
            "Company details saved successfully!"
        )

        next_url = (
            request.POST.get("next")
            or request.GET.get("next")
        )

        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)

        return redirect("edit_company")

    return render(
        request,
        "company/edit_company.html",
        {"company": company},
    )
