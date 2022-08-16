from django.db import models
from django.contrib.contenttypes.models import ContentType

from rest_framework.permissions import BasePermission

from administration.models import GeoModule, UserModule, CompanyModule, AdminModule


class IsAllowAdmin(BasePermission):
    requests_permissions = {
        "GET": "view",
        "POST": "add",
        "PUT": "change",
        "PATCH": "change",
        "DELETE": "delete",
    }
    module: models.Model = None

    def has_permission(self, request, view):
        if not request.user:
            return False

        if bool(request.user.is_superuser):
            return True

        content_type = ContentType.objects.get_for_model(self.module)
        code = self.requests_permissions.get(request.method)
        if not code:
            return False

        permission_code = f"{content_type.app_label}.{code}_{content_type.model}"
        return request.user.has_perm(permission_code)


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsGeoAdmin(IsAllowAdmin):
    module = GeoModule


class IsUserAdmin(IsAllowAdmin):
    module = UserModule


class IsCompanyAdmin(IsAllowAdmin):
    module = CompanyModule


class IsAdminAdmin(IsAllowAdmin):
    module = AdminModule
