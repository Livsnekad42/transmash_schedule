from django.db import models

from company.models import Company
from company.models.roles import Role
from notification.models import NotificationSettings
from profiles.models import Profile


class Manager(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, related_name="managers_role")
    company = models.ForeignKey(Company, related_name="managers", on_delete=models.CASCADE)
    notification_settings = models.ForeignKey(NotificationSettings, related_name="managers",
                                              null=True, on_delete=models.SET_NULL)
