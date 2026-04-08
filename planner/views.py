from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import StudyAvailabilityForm
from .models import StudyAvailability
from .services import generate_study_sessions


@login_required
def availability_view(request):
    form = StudyAvailabilityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        availability = form.save(commit=False)
        availability.user = request.user
        availability.save()
        messages.success(request, "Availability slot saved.")
        return redirect("planner:availability")

    slots = StudyAvailability.objects.filter(user=request.user)
    return render(request, "planner/availability.html", {"form": form, "slots": slots})


@login_required
def generate_plan_view(request):
    created = generate_study_sessions(request.user)
    if created:
        messages.success(request, f"Generated {len(created)} study sessions.")
    else:
        messages.warning(request, "No study sessions were generated. Add availability or upcoming tasks first.")
    return redirect("dashboard:home")
