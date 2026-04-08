from django.contrib import admin

from .models import LMSConnection, SyncLog


@admin.register(LMSConnection)
class LMSConnectionAdmin(admin.ModelAdmin):
    list_display = ("display_name", "provider", "mode", "auth_type", "user", "last_synced_at")
    list_filter = ("provider", "mode", "auth_type", "is_active")
    search_fields = ("display_name", "user__username")


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ("connection", "status", "items_imported", "started_at", "ended_at")
