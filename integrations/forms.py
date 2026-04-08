from django import forms

from .models import LMSConnection


class LMSConnectionForm(forms.ModelForm):
    class Meta:
        model = LMSConnection
        fields = (
            "display_name",
            "provider",
            "mode",
            "auth_type",
            "base_url",
            "client_id",
            "client_secret",
            "access_token",
            "is_active",
        )
        widgets = {
            "client_secret": forms.PasswordInput(render_value=True),
            "access_token": forms.PasswordInput(render_value=True),
        }
