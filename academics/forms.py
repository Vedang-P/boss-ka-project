from django import forms

from .models import Task


class ManualTaskForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Task
        fields = (
            "course",
            "title",
            "description",
            "task_type",
            "due_at",
            "weight_percent",
            "difficulty",
            "estimated_hours",
        )
