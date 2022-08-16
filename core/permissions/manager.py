from typing import Union, Any, Tuple

from django.db import models
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated

from authentication.models import User
from company.models import PermissionEnum, Company, Manager
from profiles.models import TypeUser


class ManagerPermission(IsAuthenticated):
    permissions = {
        "GET": int(PermissionEnum.READER.value),
        "POST": int(PermissionEnum.READERWRITER.value),
        "PUT": int(PermissionEnum.READERWRITER.value),
        "DELETE": int(PermissionEnum.ADMIN.value),
    }
    module_name: str = ""

    def get_permission_module(self, user: User) -> Tuple[Union[int, None], Any]:
        profile = getattr(user, "profile", None)
        if not profile:
            return None, None

        if profile.user_type != TypeUser.MANAGER.value:
            return None, None

        manager = getattr(profile, "manager", None)
        if not manager:
            return None, None

        roles = manager.roles.all()

        for _role in roles:
            permission_module = getattr(_role, self.module_name, None)
            if permission_module:
                return int(permission_module), _role

        return None, None

    def is_super_user(self, request, obj: models.Model) -> bool:
        profile = getattr(request.user, "profile", None)
        if profile and profile.pk == obj.profile.pk:
            return True

        return False

    def is_permission_obj(self, request, obj: models.Model) -> bool:
        profile = getattr(request.user, "profile", None)
        if not profile:
            return False

        manager = getattr(profile, "manager", None)
        if not manager:
            return False

        return manager.company.pk == obj.pk

    def has_permission(self, request, view) -> bool:
        if not request.user.is_authenticated:
            return False

        profile = getattr(request.user, "profile", None)
        if not profile:
            return False

        # manager = getattr(profile, "manager", None)
        # if not manager:
        #     return False

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        if self.is_super_user(request, obj):
            return True

        if not self.is_permission_obj(request, obj):
            return False

        permission, role = self.get_permission_module(request.user)
        if role is None:
            return False

        method = request.method
        if self.permissions.get(method) and self.permissions[method] >= permission:
            return True

        return False


def get_company_from_request(request) -> Company:
    profile = getattr(request.user, "profile", None)
    if not profile:
        raise exceptions.PermissionDenied(None, None)

    if profile:
        company = getattr(profile, "company", None)
        if company:
            return company

    manager = getattr(profile, "manager", None)
    if manager:
        company = getattr(manager, "company", None)
        if company:
            return company

    raise exceptions.PermissionDenied(None, None)


def get_manager(request) -> Union[Manager, None]:
    profile = getattr(request.user, "profile", None)
    if not profile:
        return None

    manager = getattr(profile, "manager", None)

    return manager
