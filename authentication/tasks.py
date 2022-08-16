import logging

import requests

try:
    from django.core.urlresolvers import reverse, reverse_lazy

except ImportError:
    from django.urls import reverse, reverse_lazy

from django.core.mail import send_mail
from django.conf import settings

from main.celery import app
from authentication.models import User


@app.task(bind=True, default_retry_delay=300, max_retries=5)
def send_verification_email(task_obj, email: str, code: str):
    if settings.DEBUG:
        print(f"send verify email code to {email}: {code}, from: {settings.EMAIL_HOST_USER}")
    send_mail('Код верификации на портале', f'Код верификации: \n {code}', settings.EMAIL_HOST_USER, [email])


@app.task(bind=True, default_retry_delay=300, max_retries=5)
def verification_sms_api(task_obj, phone: str, code: str):
    if settings.DEBUG:
        print(f"send verify phone code to {phone}: {code}")
    for i in range(3):
        resp = requests.get(settings.SMS_SEND_URL.format(phone, f"Код верификации: {code}"))
        if resp.ok:
            return
