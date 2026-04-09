from django import forms

from .models import StudyAvailability


class StudyAvailabilityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["weekday"].choices = StudyAvailability.WEEKDAY_CHOICES
        self.fields["weekday"].initial = 0
        self.fields["start_time"].widget.attrs.update({"step": 900})
        self.fields["end_time"].widget.attrs.update({"step": 900})

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and start_time >= end_time:
            self.add_error("end_time", "End time must be after start time.")
        return cleaned_data

    class Meta:
        model = StudyAvailability
        fields = ("weekday", "start_time", "end_time")
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }
