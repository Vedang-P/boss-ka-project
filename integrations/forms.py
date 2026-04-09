from django import forms

from .models import LMSConnection


class LMSConnectionForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        mode = cleaned_data.get("mode")
        auth_type = cleaned_data.get("auth_type")
        base_url = (cleaned_data.get("base_url") or "").strip()
        access_token = (cleaned_data.get("access_token") or "").strip()
        client_id = (cleaned_data.get("client_id") or "").strip()
        client_secret = (cleaned_data.get("client_secret") or "").strip()

        if mode == "live":
            if not base_url:
                self.add_error("base_url", "Base URL is required in live mode.")
            if auth_type == "token" and not access_token:
                self.add_error("access_token", "Access token is required for token auth in live mode.")
            if auth_type == "oauth":
                if not client_id:
                    self.add_error("client_id", "Client ID is required for OAuth in live mode.")
                if not client_secret:
                    self.add_error("client_secret", "Client secret is required for OAuth in live mode.")

        cleaned_data["base_url"] = base_url
        cleaned_data["access_token"] = access_token
        cleaned_data["client_id"] = client_id
        cleaned_data["client_secret"] = client_secret
        return cleaned_data

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
