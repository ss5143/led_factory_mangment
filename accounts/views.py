
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def login_user(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Empty fields check
        if not username or not password:

            return render(
                request,
                "login.html",
                {
                    "error": "Username and Password are required."
                }
            )

        # Authenticate user
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Go to requested page if available
            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")

        # Wrong username/password
        return render(
            request,
            "login.html",
            {
                "error": "Invalid Username or Password"
            }
        )

    return render(
        request,
        "login.html"
    )


def logout_user(request):

    logout(request)

    return redirect("login")
