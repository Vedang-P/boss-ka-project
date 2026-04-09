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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].empty_label = "No linked course"
        self.fields["course"].widget.attrs.update({"data-select": "course"})
        self.fields["title"].widget.attrs.update({"placeholder": "e.g. OS lab reflection"})
        self.fields["description"].widget.attrs.update(
            {
                "rows": 7,
                "placeholder": "Add context, deliverables, or submission notes.",
            }
        )
        self.fields["weight_percent"].widget.attrs.update(
            {
                "min": 0,
                "max": 100,
                "step": "0.01",
                "inputmode": "decimal",
                "placeholder": "0",
                "class": "input-no-spin",
            }
        )
        self.fields["estimated_hours"].widget.attrs.update(
            {
                "min": 0,
                "max": 99,
                "step": "0.5",
                "inputmode": "decimal",
                "placeholder": "0",
                "class": "input-no-spin",
            }
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
