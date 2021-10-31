from rest_framework.reverse import reverse
from django.conf import settings
from django.template import loader
from django.conf import settings
from .tasks import send_email


def get_user_activation_url(token):
    url = settings.FRONTEND_CONFIRM_EMAIL_URL
    return f"{url}?confirmEmailToken={token.token}"


def get_password_reset_url(user, token):
    url = settings.FRONTEND_RESET_PASSWORD_URL
    return f"{url}?changePasswordToken={token.token}&userEmail={user.email}&userUsername={user.username}"


def send_activate_account_email(user, url, request):
    template = loader.get_template("email/user_activation.html")
    context = {
        "user": user,
        "url": url,
    }
    html = template.render(context, request)
    email_subject = "Activate your account."
    send_email.delay(user.email, html, email_subject)


def send_reset_password_email(user, url, request):
    template = loader.get_template("email/user_reset_password.html")
    context = {
        "user": user,
        "reset_url": url,
        "user_host": request.get_host(),
        "user_agent": request.META["HTTP_USER_AGENT"],
        "token_expires_in_hours": int(
            settings.RESET_PASSWORD_TOKEN_MAX_AGE_DAYS.total_seconds() // 3600
        ),
        "frontend_url": settings.FRONTEND_DOMAIN_NAME,
    }
    html = template.render(context, request)
    email_subject = "Reset your password."
    send_email.delay(user.email, html, email_subject)
