from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .exceptions import ProviderError
from .forms import LMSConnectionForm
from .models import LMSConnection
from .services import sync_connection


@login_required
def connection_create(request):
    form = LMSConnectionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        connection = form.save(commit=False)
        connection.user = request.user
        connection.credential_hint = connection.masked_token
        connection.status_message = "Connection saved. Run sync to import data."
        connection.save()
        messages.success(request, "LMS connection created.")
        return redirect("dashboard:home")

    return render(request, "integrations/connection_form.html", {"form": form})


@login_required
@require_POST
def connection_sync(request, pk):
    connection = get_object_or_404(LMSConnection, pk=pk, user=request.user)
    try:
        sync_connection(connection)
        messages.success(request, f"{connection.display_name} synced successfully.")
    except ProviderError as exc:
        messages.error(request, f"Sync failed: {exc}")
    return redirect("dashboard:home")


@login_required
@require_POST
def connection_sync_all(request):
    connections = LMSConnection.objects.filter(user=request.user, is_active=True)
    if not connections.exists():
        messages.warning(request, "No active LMS connections available to sync.")
        return redirect("dashboard:home")

    success_count = 0
    failed_count = 0
    for connection in connections:
        try:
            sync_connection(connection)
            success_count += 1
        except ProviderError:
            failed_count += 1

    if failed_count == 0:
        messages.success(request, f"Synced {success_count} LMS connection(s).")
    else:
        messages.warning(
            request,
            f"Synced {success_count} connection(s). {failed_count} failed. Check status messages for details.",
        )
    return redirect("dashboard:home")


@login_required
def connection_delete(request, pk):
    """Delete an LMS connection and all its imported data."""
    connection = get_object_or_404(LMSConnection, pk=pk, user=request.user)
    if request.method == "POST":
        name = connection.display_name
        connection.delete()
        messages.success(
            request, f"Connection '{name}' and all its imported data have been removed."
        )
        return redirect("integrations:manage")
    return render(
        request,
        "integrations/connection_confirm_delete.html",
        {"connection": connection},
    )


@login_required
def manage_connections(request):
    """List all LMS connections for the user."""
    connections = request.user.lms_connections.prefetch_related("sync_logs").order_by(
        "provider", "display_name"
    )
    return render(request, "integrations/manage.html", {"connections": connections})


@login_required
@require_POST
def connection_toggle_mode(request, pk):
    """Flip a connection between demo and live mode, then re-sync."""
    connection = get_object_or_404(LMSConnection, pk=pk, user=request.user)
    new_mode = "live" if connection.mode == "demo" else "demo"
    connection.mode = new_mode
    connection.last_synced_at = None
    connection.status_message = (
        f"Switched to {connection.get_mode_display()} mode. Sync to refresh data."
    )
    connection.save(
        update_fields=["mode", "last_synced_at", "status_message", "updated_at"]
    )

    # Auto-sync so the dashboard reflects the new mode immediately
    try:
        sync_connection(connection)
        messages.success(
            request,
            f"{connection.display_name} switched to {connection.get_mode_display()} mode and synced.",
        )
    except ProviderError as exc:
        messages.warning(
            request,
            f"{connection.display_name} switched to {connection.get_mode_display()} mode, "
            f"but sync failed: {exc}",
        )
    return redirect("integrations:manage")
