from datetime import timedelta
from typing import Tuple

from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rest_framework import serializers

from administration.serializers import GroupSerializer
from company.serializers import RoleSerializer
from core.app_services.recapcha import google_capcha
from core.mixins.valid_user_password import ValidUserPasswordMixin
from core.serialize_fields.phone import PhoneField
from core.utils import convert_timedelta_to_str
from .services.anti_bruteforce import AntiBruteForce, ResultStatus
from .services.auth_service import create_code, set_verify_code_from_redis, is_valid_code, is_live_phone_code

from .models import AuthPhoneModel
from .services.jwt_helpers import decode_token2dict
from .tasks import send_verification_email, verification_sms_api

User = get_user_model()

# Время жизни кода из СМС
SMS_CODE_EXPIRATION_DELTA = getattr(settings, "SMS_CODE_EXPIRATION_DELTA", timedelta(seconds=180))
SMS_REFRESH_CODE_EXPIRATION = getattr(settings, "SMS_REFRESH_CODE_EXPIRATION", timedelta(seconds=180))
EMAIL_CODE_EXPIRATION_DELTA = getattr(settings, "EMAIL_CODE_EXPIRATION_DELTA", timedelta(minutes=10))
COUNT_FAILED_ATTEMPT = getattr(settings, "COUNT_FAILED_ATTEMPT", 10)
BAN_TIME = getattr(settings, "BAN_TIME", timedelta(minutes=30))


class ProfileDataSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    last_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    patronymic = serializers.CharField(max_length=255, required=False, allow_null=True)
    avatar = serializers.ImageField(read_only=True)
    user_type = serializers.CharField(read_only=True)
    background_tree = serializers.CharField(read_only=True)

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'patronymic',
            'avatar',
            'user_type',
            'background_tree',
        )


class CompanyDataSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    logo = serializers.ImageField(read_only=True)

    class Meta:
        fields = (
            'name',
            'logo',
        )


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_null=True, write_only=True)
    phone = PhoneField(required=False, allow_null=True, max_length=25, min_length=10, write_only=True)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    # captcha = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'phone',
            'password',
            # 'captcha',
        )

    def validate(self, attrs):
        captcha = attrs.pop("captcha", None)

        # регистрация
        if not attrs.get("password"):
            raise serializers.ValidationError(_('Required field "password".'))

        if not attrs.get("email") and not attrs.get("phone"):
            raise serializers.ValidationError(_('Required field "email" or "phone".'))

        registration_field = "email" if attrs.get("email") else "phone"
        self.context["registration_field"] = registration_field

        # chek already exists user
        try:
            user = User.model_objects.get(**{registration_field: attrs[registration_field]})

        except User.DoesNotExist:
            user = None

        self.instance = user

        if user:
            if user.is_active:
                raise serializers.ValidationError(_(f'User with this {registration_field} already exists.'))

            else:
                checker = AntiBruteForce(f"registration_{registration_field}")
                result_checker, status = checker.check(attrs[registration_field])
                if status == ResultStatus.BAN:
                    raise serializers.ValidationError(_(f'Account temporarily blocked, please try again in '
                                                        f'{convert_timedelta_to_str(BAN_TIME)} minutes.'), "error")

        # TODO: восстановить после реализации пуш уведомлений
        # if not captcha:
        #     raise serializers.ValidationError(_('Required field "captcha".'))
        #
        # if not google_capcha(captcha):
        #     raise serializers.ValidationError(_('Captcha not passed.'))

        return attrs

    def send_code_email(self, user: User) -> None:
        code = set_verify_code_from_redis(user.pk, EMAIL_CODE_EXPIRATION_DELTA.seconds, 6)
        send_verification_email.delay(user.email, code)

    def send_code_phone(self, user: User) -> None:
        code = create_code()
        verification_sms_api.delay(user.phone, code)
        AuthPhoneModel.objects.create(user=user, code=f"{user.phone}_{code}")

    def send_verify_code(self, user: User):
        if user.email:
            self.send_code_email(user)

        if user.phone:
            self.send_code_phone(user)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        self.send_verify_code(user)
        return user

    def update(self, instance, validated_data):
        self.send_verify_code(instance)
        return instance


class VerifyUserSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(write_only=True)
    email = serializers.EmailField(required=False, write_only=True)
    phone = PhoneField(required=False, max_length=25, min_length=8, write_only=True)
    token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    profile = ProfileDataSerializer(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'phone',
            'code',
            'token',
            'refresh_token',
            'profile',
            'is_superuser',
        )

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("phone"):
            raise serializers.ValidationError(_('Required field "email" or "phone".'))

        registration_field = "email" if attrs.get("email") else "phone"
        try:
            self.instance = User.model_objects.get(**{registration_field: attrs[registration_field]})

        except User.DoesNotExist:
            raise serializers.ValidationError(
                _(f'Invalid "{registration_field}".'))

        code = attrs.get('code')
        if not code:
            raise serializers.ValidationError(
                _('To complete the authorization, enter the code.'))

        if registration_field == "email":
            is_verify, message = is_valid_code(self.instance.pk, code)
            if not is_verify:
                if message.status == ResultStatus.BAN:
                    raise serializers.ValidationError(_(f'Account temporarily blocked, please try again in '
                                                        f'{convert_timedelta_to_str(BAN_TIME)} minutes.'))

                else:
                    raise serializers.ValidationError(_('Invalid verification code.'))

        else:
            is_confirm, message = self.confirm_validate(code)
            if not is_confirm:
                if message.status == ResultStatus.BAN:
                    raise serializers.ValidationError(_(f'Account temporarily blocked, please try again in '
                                                        f'{convert_timedelta_to_str(BAN_TIME)} minutes.'))

        attrs["token"] = self.instance.token
        attrs["refresh_token"] = self.instance.refresh_token
        attrs["is_superuser"] = self.instance.is_superuser

        profile = getattr(self.instance, "profile", None)
        if profile:
            attrs["profile"] = profile

        return attrs

    def update(self, instance, validated_data):
        instance.is_active = True
        instance.save()
        return instance

    @method_decorator(AntiBruteForce("confirm_validate"))
    def confirm_validate(self, code: str) -> Tuple[bool, str]:
        try:
            auth_phone = AuthPhoneModel.objects.filter(code=f"{self.instance.phone}_{code}",
                                                       user__id=self.instance.pk).get()

        except AuthPhoneModel.DoesNotExist:
            return False, _("Invalid verification code.")

        auth_phone.delete()

        if not is_live_phone_code(self.instance.pk, auth_phone.created_at, SMS_CODE_EXPIRATION_DELTA):
            return False, _("Code is outdated.")

        return True, ""


class LoginSerializer(serializers.Serializer, ValidUserPasswordMixin):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    phone = PhoneField(max_length=25, min_length=10, required=False, write_only=True)
    email = serializers.EmailField(required=False, write_only=True)
    token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    profile = ProfileDataSerializer(read_only=True)
    company = CompanyDataSerializer(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    # captcha = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'phone',
            'password',
            'token',
            'refresh_token',
            'profile',
            'company',
            'roles',
            'is_superuser',
            # 'captcha',
        )

    def validate(self, attrs):
        email = attrs.get('email', None)
        phone = attrs.get('phone', None)
        password = attrs.get('password', None)
        captcha = attrs.pop("captcha", None)

        # TODO: восстановить после реализации пуш уведомлений
        # if not captcha:
        #     raise serializers.ValidationError(_('Required field "captcha".'))
        #
        # if not google_capcha(captcha):
        #     raise serializers.ValidationError(_('Captcha not passed.'))

        if not phone and not email:
            raise serializers.ValidationError(_('Must include "phone" or "email".'))

        if password is None:
            raise serializers.ValidationError(
                _('A password is required to log in.')
            )

        user = self.get_valid_password(password, email, phone)
        if user is None:
            raise serializers.ValidationError(
                _('A user with this email or phone and password was not found.')
            )

        if not user.is_active:
            raise serializers.ValidationError(
                _('This user has been deactivated.')
            )

        user_data = {
            'token': user.token,
            'refresh_token': user.refresh_token,
            'is_superuser': user.is_superuser,
        }

        if user.is_staff:
            user_data["groups"] = list(map(lambda g: GroupSerializer(g).data, user.groups.all()))

        profile = getattr(user, "profile", None)
        if profile:
            user_data["profile"] = profile
            if getattr(profile, "company", None):
                user_data["company"] = profile.company

            if getattr(profile, "manager", None):
                user_data["company"] = profile.manager.company,
                user_data["roles"] = profile.manager.roles.all()

        return user_data


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(required=True)
    profile = ProfileDataSerializer(read_only=True)
    company = CompanyDataSerializer(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    class Meta:
        fields = (
            'token',
            'refresh_token',
            'profile',
            'company',
            'roles',
            'is_superuser',
        )

    def validate(self, attrs):
        refresh_token = attrs.get("refresh_token")

        if not refresh_token:
            raise serializers.ValidationError(
                _('Not received refresh_token.')
            )

        payload = decode_token2dict(refresh_token)
        if not payload:
            raise serializers.ValidationError(
                _('Permission denied.')
            )

        try:
            self.instance = User.model_objects.get(id=payload.get("id"))

        except User.DoesNotExist:
            raise serializers.ValidationError(
                _('Permission denied.')
            )

        if self.instance is None or not self.instance.is_active:
            raise serializers.ValidationError(
                _('This user has been deactivated.')
            )

        return attrs

    def to_representation(self, instance):
        data = {
            'token': instance.token,
            'refresh_token': instance.refresh_token,
            'is_superuser': instance.is_superuser,
        }

        if instance.is_staff:
            data["groups"] = list(map(lambda g: GroupSerializer(g).data, instance.groups.all()))

        profile = getattr(self.instance, "profile", None)
        if profile:
            data["profile"] = ProfileDataSerializer(profile).data
            if getattr(profile, "company", None):
                data["company"] = CompanyDataSerializer(profile.company).data

            if getattr(profile, "manager", None):
                data["company"] = CompanyDataSerializer(profile.manager.company).data,
                data["roles"] = list(map(lambda r: RoleSerializer(r).data, profile.manager.roles.all()))

        return data


class RestorePasswordSerializer(serializers.ModelSerializer):
    phone = PhoneField(max_length=25, min_length=10, required=False, write_only=True)
    email = serializers.EmailField(required=False, write_only=True)
    # captcha = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'phone',
            'email',
            # 'captcha',
        )

    def validate(self, attrs):
        phone = attrs.get("phone")
        email = attrs.get("email")
        captcha = attrs.pop("captcha", None)

        # if not captcha:
        #     raise serializers.ValidationError(_('Required field "captcha".'))
        # if not google_capcha(captcha):
        #     raise serializers.ValidationError(_('Captcha not passed.'))

        if not phone and not email:
            raise serializers.ValidationError(_('Must include "phone" or "email".'))

        if phone:
            try:
                user = User.model_objects.get(phone=phone)

            except User.DoesNotExist:
                raise serializers.ValidationError(
                    _('Permission denied.')
                )
            code = set_verify_code_from_redis(user.pk, SMS_CODE_EXPIRATION_DELTA.seconds, 6)
            verification_sms_api.delay(user.phone, code)

            return {}

        try:
            user = User.model_objects.get(email=email)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                _('Permission denied.')
            )
        code = set_verify_code_from_redis(user.pk, EMAIL_CODE_EXPIRATION_DELTA.seconds, 12)
        send_verification_email.delay(user.email, code)

        return {}


class ConfirmRestorePasswordSerializer(serializers.ModelSerializer):
    phone = PhoneField(max_length=25, min_length=10, required=False, write_only=True)
    email = serializers.EmailField(required=False, write_only=True)
    code = serializers.CharField(max_length=25, write_only=True)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = (
            'phone',
            'email',
            'code',
            'password',
        )

    def validate(self, attrs):
        phone = attrs.get("phone")
        email = attrs.get("email")
        code = attrs.get("code")
        password = attrs.get("password")
        user = None

        if not code:
            raise serializers.ValidationError(_('To complete the restore password, enter the code.'))

        if not password:
            raise serializers.ValidationError(_('To complete the restore password, enter the new password.'))

        if not phone and not email:
            raise serializers.ValidationError(_('Must include "phone" or "email".'))

        if phone:
            try:
                user = User.model_objects.get(phone=phone)

            except User.DoesNotExist:
                user = None

        elif email:
            try:
                user = User.model_objects.get(email=email)

            except User.DoesNotExist:
                user = None

        if not user:
            raise serializers.ValidationError(
                _('Permission denied.')
            )

        self.instance = user

        is_verify, message = is_valid_code(self.instance.pk, code)
        if not is_verify:
            if message.status == ResultStatus.BAN:
                raise serializers.ValidationError(_(f'Account temporarily blocked, please try again in '
                                                    f'{convert_timedelta_to_str(BAN_TIME)} minutes.'))

            else:
                raise serializers.ValidationError(_('Invalid verification code.'))

        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.pop('password', None)

        instance.set_password(new_password)
        instance.save()

        return instance

