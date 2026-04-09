from django import forms

from academics.models import Course


class GradePredictionFilterForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = user.courses.order_by("title")
        self.fields["course"].empty_label = "All courses"
