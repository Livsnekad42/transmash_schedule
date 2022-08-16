from datetime import timedelta
from typing import Union

from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.utils.timezone import now

from company.models import Manager, Company, PermissionEnum
from core.enums.status import StatusOrder
from notification.services.send_notify import send_to_email, send_to_sms
from main.celery import app


@app.task(bind=True, default_retry_delay=300, max_retries=5)
def send_email(task_obj, email: str, message: str):
    send_to_email(email, message)


@app.task(bind=True, default_retry_delay=300, max_retries=5)
def send_sms(task_obj, phone: str, message: str):
    send_to_sms(phone, message)

