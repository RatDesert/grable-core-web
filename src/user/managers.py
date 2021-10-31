from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom User model manager."""

    def create_user(self, **kwargs):
        email, password = kwargs.get("email"), kwargs.get("password")

        if not email:
            raise ValueError("The Email must be set")

        if not password:
            raise ValueError("The password must be set")

        email = self.normalize_email(email)
        user = self.model(**kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, **kwargs):
        is_superuser, is_staff = kwargs.get("is_superuser", False), kwargs.get(
            "is_staff", False
        )

        if not is_superuser:
            raise ValueError("The Email must be set")

        if not is_staff:
            raise ValueError("The password must be set")

        return self.create_user(**kwargs)

    def change_password(self, token, password):
        user = self.select_related("reset_password_token").get(
            reset_password_token__token=token,
            reset_password_token__exp_date__gt=timezone.now(),
        )
        user.set_password(password)
        #hack for signals
        user.save(update_fields=['password'])
        user.reset_password_token.delete()

        return user


class ActivateUserTokenManager(models.Manager):
    def activate_user(self, **kwargs):
        token = self.select_related("user").get(**kwargs, expires_at__gt=timezone.now())
        user = token.user
        user.is_active = True
        user.save()
        token.delete()
