import time

from django.test import TestCase
from django.contrib.auth import get_user_model

from authentication.serializers import RegistrationSerializer, RestorePasswordSerializer, \
    ConfirmRestorePasswordSerializer

User = get_user_model()


class SerializerTests(TestCase):
    def test_login_serializer_from_api(self):
        data = {
            "password": "123456qw",
            "email": "mail@mail.ru",
        }

        serializer = RegistrationSerializer(data=data)

        is_valid = serializer.is_valid()
        if not is_valid:
            print(serializer.errors)
        self.assertTrue(is_valid)

    def test_unique(self):
        users = [
            {
                "password": "123456we",
                "email": "mail1@mail.ru",
                "phone": None
            },
            {
                "password": "123456rte",
                "email": "mail1@mail.ru",
                "phone": None
            }
        ]

        for user in users:
            serializer = RegistrationSerializer(data=user)
            is_valid = serializer.is_valid()
            if not is_valid:
                print(serializer.errors)
            self.assertTrue(is_valid)

    def test_restore_password(self):
        print("=" * 80)
        print("restore password")
        data = {
            "password": "123456qw",
            "email": "press.83@list.ru",
        }

        serializer = RegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        if not is_valid:
            print("registration serializer error: ", serializer.errors)
        self.assertTrue(is_valid)
        serializer.save()

        serializer = RestorePasswordSerializer(data=data)
        is_valid = serializer.is_valid()
        if not is_valid:
            print("restore serializer error: ", serializer.errors)
        self.assertTrue(is_valid)

        code = input("please enter code from sms: \n")
        data["code"] = code
        serializer = ConfirmRestorePasswordSerializer(data=data)
        is_valid = serializer.is_valid()
        if not is_valid:
            print("confirm serializer error: ", serializer.errors)
        self.assertTrue(is_valid)
        serializer.save()


