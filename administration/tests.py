import operator
from functools import reduce

from django.db.models import Q
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission

from administration.serializers import GroupSerializer, PermissionSerializer, AdminProfileSerializer
from administration.services.constants import ADMIN_MODULES


class SerializerTests(TestCase):
    def create_groups(self):
        permission_ids = []
        for _module in ADMIN_MODULES:
            content_type = ContentType.objects.get_for_model(_module["model"])
            permissions = Permission.objects.filter(content_type=content_type)
            for _perm in permissions:
                permission_ids.append(_perm.pk)

        data = {
            "name": "test_group",
            "permission_ids": permission_ids,
        }

        # create
        serializer = GroupSerializer(data=data)
        return serializer, data

    def test_create_and_update_group(self):
        print("=" * 80)
        serializer, data = self.create_groups()
        # create
        is_valid = serializer.is_valid()
        if not is_valid:
            print("error test_create_group: ", serializer.errors)

        self.assertTrue(is_valid)

        instance = serializer.save()
        data = serializer.data
        print("create data: ", data)

        data["permission_ids"] = [data["permission_ids"][0]]

        # update
        serializer = GroupSerializer(instance, data=data)
        is_valid = serializer.is_valid()
        if not is_valid:
            print("error test_update_group: ", serializer.errors)

        self.assertTrue(is_valid)

        serializer.save()
        data = serializer.data
        print("update data: ", data)

    def test_get_list_permissions(self):
        print("=" * 80)
        permissions = Permission.objects.filter(
            reduce(
                operator.or_,
                (Q(codename__contains=item["model"].model_name()) for item in ADMIN_MODULES)
            )
        )
        data = []
        for _module in ADMIN_MODULES:
            _permissions = []
            for _perm in permissions:
                if _module["model"].model_name() == _perm.content_type.model:
                    _permissions.append(
                        PermissionSerializer(_perm).data
                    )

            data.append({
                "module": _module["title"],
                "permissions": _permissions,
            })

        self.assertTrue(len(data) == 4)

        print("test_get_list_permissions: ", data)

    def test_create_admin_manager(self):
        print("=" * 80)
        serializer, _ = self.create_groups()
        serializer.is_valid(raise_exception=True)
        group_instance = serializer.save()
        data_user = {
            "email": "mail@mail.ru",
            "password": "1234qwer",
            "groups_ids": [group_instance.pk]
        }

        data = {
            "user": data_user,
            "first_name": "Test",
            "last_name": "Testovich",
        }

        serializer = AdminProfileSerializer(data=data)
        is_valid = serializer.is_valid()
        if not is_valid:
            print("error test_create_admin_manager: ", serializer.errors)

        self.assertTrue(is_valid)

        serializer.save()
        data = serializer.data
        print("test_create_admin_manager data: ", data)



