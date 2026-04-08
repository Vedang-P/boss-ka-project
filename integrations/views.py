from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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
def connection_sync(request, pk):
    connection = get_object_or_404(LMSConnection, pk=pk, user=request.user)
    try:
        sync_connection(connection)
        messages.success(request, f"{connection.display_name} synced successfully.")
    except ProviderError as exc:
        messages.error(request, f"Sync failed: {exc}")
    return redirect("dashboard:home")
