from django.db import models


class NotificationSettings(models.Model):
    is_email = models.BooleanField(default=True)
    is_phone = models.BooleanField(default=False)
