import os.path
from dataclasses import dataclass
from enum import Enum
from typing import Union

from django.conf import settings
from jinja2 import Environment, FileSystemLoader, select_autoescape

from notification.tasks import send_email, send_sms

JINJA_ENV = Environment(
    loader=FileSystemLoader(os.path.join(settings.BASE_DIR, 'templates/alerts')),
    autoescape=select_autoescape(['html', 'xml'])
)


class AlertType(Enum):
    EMAIL = "1"
    SMS = "2"
    PUSH = "3"


@dataclass
class Message:
    email: str
    sms: str


class NotifyTemplate:
    template: str

    def __init__(self, template: str = None):
        if template:
            self.template = template

    def send_alert(self, address: str, alert_type: AlertType, **kwargs):
        message = self.render(alert_type, **kwargs)

        if alert_type == AlertType.EMAIL:
            send_email.delay(address, message)

        elif alert_type == AlertType.SMS:
            send_sms.delay(address, message)

    def render(self, alert_type: AlertType, **kwargs) -> Union[str, None]:
        if alert_type == AlertType.EMAIL:
            return self.render_email(**kwargs)

        elif alert_type == AlertType.SMS:
            return self.render_sms(**kwargs)

        return None

    def render_email(self, **kwargs):
        template = JINJA_ENV.get_template(os.path.join("email", self.template))
        return template.render(**kwargs)

    def render_sms(self, **kwargs):
        template = JINJA_ENV.get_template(os.path.join("sms", self.template))
        return template.render(**kwargs)

