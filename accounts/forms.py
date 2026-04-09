from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from zoneinfo import available_timezones

from .models import StudentProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("timezone", "preferred_daily_study_hours", "course_load_note")
        widgets = {
            "timezone": forms.TextInput(attrs={"placeholder": "Asia/Kolkata"}),
            "preferred_daily_study_hours": forms.NumberInput(attrs={"min": 1, "max": 16}),
            "course_load_note": forms.TextInput(
                attrs={"placeholder": "e.g. Final semester, heavy workload"}
            ),
        }

    def clean_timezone(self):
        timezone_name = (self.cleaned_data.get("timezone") or "").strip() or "Asia/Kolkata"
        if timezone_name not in available_timezones():
            raise forms.ValidationError("Enter a valid IANA timezone, for example Asia/Kolkata.")
        return timezone_name
