import requests
from django.conf import settings
from django.core.mail import send_mail


def send_to_email(email: str, message: str):
    send_mail(message, settings.EMAIL_HOST_USER, [email])


def send_to_sms(phone: str, message: str, count_attempts: int = 3):
    for i in range(count_attempts):
        resp = requests.get(settings.SMS_SEND_URL.format(phone, message))
        if resp.ok:
            return
