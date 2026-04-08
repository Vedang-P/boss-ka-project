from django import forms

from .models import StudyAvailability


class StudyAvailabilityForm(forms.ModelForm):
    class Meta:
        model = StudyAvailability
        fields = ("weekday", "start_time", "end_time")
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }
