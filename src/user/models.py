import secrets
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager, ActivateUserTokenManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(
        unique=True, max_length=64, validators=[MinLengthValidator(4)]
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    premium_expires_at = models.DateField(null=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "username"

    objects = UserManager()

    class Meta:
        db_table = "users"
        constraints = [
            # Superuser is always staff
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_superuser_is_staff",
                check=(~models.Q(is_superuser=True, is_staff=False)),
            )
        ]

    def __str__(self):
        return self.username

    @property
    def is_premium(self) -> bool:
        if self.premium_expires_at is None:
            return False

        if self.is_staff or self.is_superuser:
            return True

        return timezone.now() < self.premium_expires_at


def generate_token64():
    return secrets.token_urlsafe(64)


def get_email_token_exp_date():
    return timezone.now() + settings.EMAIL_TOKEN_MAX_AGE_DAYS


class ActivateUserToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="email_activation_token"
    )
    token = models.CharField(max_length=96, default=generate_token64)
    expires_at = models.DateTimeField(default=get_email_token_exp_date)

    objects = ActivateUserTokenManager()

    class Meta:
        db_table = "activate_user_tokens"

    def __str__(self):
        return self.token


def get_reset_token_exp_date():
    return timezone.now() + settings.RESET_PASSWORD_TOKEN_MAX_AGE_DAYS


class ResetPasswordToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="reset_password_token"
    )
    token = models.CharField(max_length=96, default=generate_token64)
    expires_at = models.DateTimeField(default=get_reset_token_exp_date)

    class Meta:
        db_table = "reset_password_tokens"

    def __str__(self):
        return self.token


class UserEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event")
    name = models.CharField(max_length=32)
    details = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "user_events"

    def __str__(self):
        return self.name
