from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


@shared_task
def send_email(email, html, subject):
    text = strip_tags(html)
    email = EmailMultiAlternatives(subject, text, to=[email])
    email.attach_alternative(html, "text/html")
    email.send()
