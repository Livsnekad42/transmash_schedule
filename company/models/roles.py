from django.db import models

from company.models import Company
from core.enums.permission import PermissionEnum
from employee.models import Branch


class Role(models.Model):
    PERMISSIONS = (
        (PermissionEnum.ADMIN.value, "admin"),
        (PermissionEnum.READER.value, "read"),
        (PermissionEnum.READERWRITER.value, "read_write"),
        (PermissionEnum.NOT_ALLOW.value, "not_allow")
    )

    name = models.CharField(max_length=250)
    module_admin = models.CharField(max_length=3, choices=PERMISSIONS, default=PermissionEnum.NOT_ALLOW.value)
    module_manager = models.CharField(max_length=3, choices=PERMISSIONS, default=PermissionEnum.NOT_ALLOW.value)
    module_report = models.CharField(max_length=3, choices=PERMISSIONS, default=PermissionEnum.READER.value)
    module_services = models.CharField(max_length=3, choices=PERMISSIONS, default=PermissionEnum.READER.value)
    module_orders = models.CharField(max_length=3, choices=PERMISSIONS, default=PermissionEnum.NOT_ALLOW.value)
    module_landing = models.CharField(max_length=3, choices=PERMISSIONS, default=PermissionEnum.NOT_ALLOW.value)
    module_tasks = models.CharField(max_length=3, choices=PERMISSIONS, default=PermissionEnum.NOT_ALLOW.value)
    company = models.ForeignKey(Company, related_name="roles", on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name="roles", null=True, on_delete=models.SET_NULL)
