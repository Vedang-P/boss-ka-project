from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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


@login_required
def profile_view(request):
    profile = request.user.student_profile
    if request.method == "POST":
        tz = request.POST.get("timezone", "Asia/Kolkata").strip()
        daily_hours = request.POST.get("preferred_daily_study_hours", "2").strip()
        course_load_note = request.POST.get("course_load_note", "").strip()
        # basic validation
        try:
            daily_hours_int = max(1, min(16, int(daily_hours)))
        except ValueError:
            daily_hours_int = 2
        profile.timezone = tz or "Asia/Kolkata"
        profile.preferred_daily_study_hours = daily_hours_int
        profile.course_load_note = course_load_note
        profile.save()
        from django.contrib import messages

        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"profile": profile})
