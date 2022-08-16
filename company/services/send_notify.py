from django.conf import settings
from django.urls import reverse

from company.models import Manager, Company
from notification.services.send_notify import send_to_email


message_created_manager = f"Вы авторизованы на портале {settings.APP_HOST} как менеджер компании %s. \n" \
                          f"Для аутентификации пройдите по ссылке: {reverse('authentication:login')}"


def send_to_manager_created(company: Company, manager: Manager):
    send_to_email.delay(manager.user.email, message_created_manager % company.name)
