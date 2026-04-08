from django.contrib.auth.models import User
from django.db import models


class LMSConnection(models.Model):
    PROVIDER_CHOICES = (
        ("canvas", "Canvas"),
        ("blackboard", "Blackboard"),
    )
    MODE_CHOICES = (
        ("demo", "Demo"),
        ("live", "Live"),
    )
    AUTH_CHOICES = (
        ("oauth", "OAuth"),
        ("token", "Token"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lms_connections")
    display_name = models.CharField(max_length=120)
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    mode = models.CharField(max_length=16, choices=MODE_CHOICES, default="demo")
    auth_type = models.CharField(max_length=16, choices=AUTH_CHOICES, default="token")
    base_url = models.URLField(blank=True)
    client_id = models.CharField(max_length=255, blank=True)
    client_secret = models.CharField(max_length=255, blank=True)
    access_token = models.CharField(max_length=255, blank=True)
    credential_hint = models.CharField(max_length=255, blank=True)
    status_message = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("provider", "display_name")

    def __str__(self):
        return f"{self.display_name} ({self.get_provider_display()})"

    @property
    def masked_token(self):
        if not self.access_token:
            return ""
        return f"{self.access_token[:4]}...{self.access_token[-4:]}"


class SyncLog(models.Model):
    STATUS_CHOICES = (
        ("started", "Started"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    connection = models.ForeignKey(LMSConnection, on_delete=models.CASCADE, related_name="sync_logs")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="started")
    message = models.CharField(max_length=255, blank=True)
    items_imported = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-started_at",)

    def __str__(self):
        return f"{self.connection.display_name} - {self.status}"
