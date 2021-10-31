from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import crypto, timezone
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


def get_session_key() -> str:
    return crypto.get_random_string(64)


def get_session_expire_date() -> datetime:
    return timezone.now() + settings.AUTH_REFRESH_MAX_AGE_SEC


class RefreshSession(models.Model):
    id = models.AutoField(primary_key=True)
    session_key = models.CharField(_("Session Key"), max_length=96, default=get_session_key)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="refresh_sessions"
    )
    expires_at = models.DateTimeField(_("Expire Date"), default=get_session_expire_date)
    http_user_agent = models.TextField(_("HTTP User Agent"), null=True)
    remote_addr = models.GenericIPAddressField(_("Remote IP"), null=True)
    remote_host = models.TextField(_("Remote Host"), null=True)

    class Meta:
        db_table = "refresh_sessions"
        verbose_name = _("Refresh Session")
        verbose_name_plural = _("Refresh Sessions")


@receiver(post_save, sender=RefreshSession)
def session_limit_reached(sender, instance, created, **kwargs):
    if created:
        q = RefreshSession.objects.filter(user=instance.user)
        if len(q) >= 6:
            q.filter(~Q(id=instance.id)).delete()
