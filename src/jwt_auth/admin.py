from django.contrib import admin
from .models import RefreshSession


@admin.register(RefreshSession)
class RemoteSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "expires_at", "remote_addr", "user")
    readonly_fields = [f.name for f in RefreshSession._meta.fields]
    fields = [f.name for f in RefreshSession._meta.fields]
