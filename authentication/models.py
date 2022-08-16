from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel
from .services.jwt_helpers import create_token, create_token_from_dict


class UserManager(BaseUserManager):
    def create_user(self, password, email=None, phone=None):
        if email is None and phone is None:
            raise TypeError('Users must have an email address or phone.')

        if password is None:
            raise TypeError('Users must have an password.')

        validate_data = {
            "email": self.normalize_email(email) if email else None,
            "phone": phone,
        }

        user = self.model(**validate_data)
        user.set_password(password)
        user.save()

        return user

    def create_manager(self, password, email=None, phone=None, is_superuser=False):
        if email is None and phone is None:
            raise TypeError('Users must have an email address or phone.')

        if password is None:
            raise TypeError('Users must have an password.')

        if email:
            validate_data = {
                "email": self.normalize_email(email),
            }
        else:
            validate_data = {
                "phone": phone,
            }

        user = self.model(**validate_data)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = is_superuser
        user.save()

        return user

    def create(self, email, phone, password=None):
        if not email and not phone:
            raise TypeError('Users must have an email address or phone.')

        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, phone=phone)
        if password:
            user.set_password(password)

        user.save()

        return user

    def create_phone(self, phone, password=None):
        if not phone:
            raise TypeError('Users must have an email address or phone.')

        user = self.model(phone=phone)
        if password:
            user.set_password(password)

        user.save()

        return user

    def create_superuser(self, email, password):
        from profiles.models import TypeUser
        if password is None:
            raise TypeError('Superusers must have a password.')
        
        user = self.create_user(**{"email": email, "password": password})
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()

        user.profile.user_type = TypeUser.ADMIN.value
        user.profile.save()
        
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True, null=True)
    phone = models.CharField(db_index=True, unique=True, max_length=25, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['email']

    objects = UserManager()
    model_objects = models.Manager()

    def __str__(self):
        return self.email

    @property
    def token(self) -> str:
        return create_token(self)

    @property
    def refresh_token(self) -> str:
        return create_token_from_dict({
            "id": self.pk
        })

    def get_full_name(self) -> str:
        return f"{self.email} {self.phone}"

    def get_short_name(self) -> str:
        return f"{self.email} {self.phone}"
    
    
class AuthPhoneModel(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField("Код СМС", max_length=25)
