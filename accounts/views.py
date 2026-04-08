from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import SignUpForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard:home")

    return render(request, "registration/signup.html", {"form": form})
