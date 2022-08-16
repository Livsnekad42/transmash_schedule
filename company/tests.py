import json

from django.test import TestCase
from django.contrib.auth import get_user_model

from authentication.serializers import RegistrationSerializer, LoginSerializer, RefreshTokenSerializer
from company.serializers import CompanySerializer, ManagerSerializer, RoleSerializer

User = get_user_model()


class SerializerTests(TestCase):

    def create_role(self, company_pk: int):
        role_serializer = RoleSerializer(data={
            "name": "new_role",
            "company": company_pk
        })
        role_serializer.is_valid(raise_exception=True)
        role_serializer.save()
        return role_serializer

    def test_create_company(self):
        data = {
            "password": "123456qw",
            "email": "mail@mail.ru",
        }

        user = User.objects.create_user(**data)
        user.is_active = True
        user.is_staff = False
        user.save()

        print("=" * 80)
        login_serializer = LoginSerializer(data=data)
        login_serializer.is_valid(raise_exception=True)
        print("user login_serializer.data: ", json.dumps(login_serializer.data))
        print()

        company_serializer = CompanySerializer(data={"name": "RoaGa i KoPiTa"}, context={"profile": user.profile})
        is_valid = company_serializer.is_valid()
        if not is_valid:
            print("[!] company_serializer not valid", company_serializer.errors)

        self.assertTrue(is_valid)

        company_serializer.save()

        print("[!] company_serializer.data: ", company_serializer.data)
        print("=" * 80)
        login_serializer = LoginSerializer(data=data)
        login_serializer.is_valid(raise_exception=True)
        print("company login_serializer.data: ", json.dumps(login_serializer.data))
        print()

        refresh_serializer = RefreshTokenSerializer(data=login_serializer.data)
        is_valid = refresh_serializer.is_valid()
        if not is_valid:
            print("[!] refresh_serializer not valid", refresh_serializer.errors)

        self.assertTrue(is_valid)

        print("=" * 80)
        print("company refresh_serializer.data: ", json.dumps(refresh_serializer.data))
        print()

        role_serializer = self.create_role(company_serializer.instance.pk)
        manager_data = {
            "user": {
                "password": "123456qw",
                "email": "",
                "phone": "903945953424",
            },
            "profile": {"first_name": "Henry", },
            "company": company_serializer.instance.pk,
            "role_pk": [role_serializer.instance.pk, ],
            "notification_settings": {
                "is_email": True,
                "is_phone": False,
            },
        }

        serializer_manager = ManagerSerializer(data=manager_data)
        is_valid = serializer_manager.is_valid()
        if not is_valid:
            print("[!] serializer_manager_data not valid", serializer_manager.errors)

        self.assertTrue(is_valid)

        serializer_manager.save()

        serializer_manager2 = ManagerSerializer(data=manager_data)
        is_valid = serializer_manager2.is_valid()
        if not is_valid:
            print("[!] serializer_manager_data2 not valid", serializer_manager2.errors)

        self.assertTrue(not is_valid)

        print("=" * 80)
        print("create serializer_manager_data.data: ", json.dumps(serializer_manager.data))
        print()

        manager_data["user"]["email"] = "newEmail@mail.com"
        manager_data["user"]["phone"] = ""
        manager_data["profile"]["first_name"] = "O'Henry"
        serializer_manager = ManagerSerializer(serializer_manager.instance, data=manager_data)
        is_valid = serializer_manager.is_valid()
        if not is_valid:
            print("[!] serializer_manager_data 3 not valid", serializer_manager.errors)

        self.assertTrue(is_valid)

        serializer_manager.save()

        print("=" * 80)
        print("update serializer_manager_data.data: ", json.dumps(serializer_manager.data))
        print()




