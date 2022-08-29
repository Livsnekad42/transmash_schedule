from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from rest_framework import serializers

from authentication.models import User
from company.models import Company, Role, Branch, Manager, PermissionEnum, OrganizationalLegalForm
from core.fields import Empty
from core.converters.images import get_img_from_data_url
from geo_city.models import Address
from geo_city.serializers import AddressSerializer
from notification.models import NotificationSettings
from notification.serializers import NotificationSettingsSerializer
from notification.services.alerts import AlertType
from notification.services.templates import ALERTS
from profiles.models import TypeUser
from profiles.serializers import ProfileSerializer


class OrganizationalLegalFormSerializer(serializers.ModelSerializer):
    directory_version = serializers.CharField(max_length=6, allow_null=True, allow_blank=True)
    code = serializers.CharField(max_length=15, allow_null=True, allow_blank=True)
    full = serializers.CharField(max_length=150)
    short = serializers.CharField(max_length=10)

    class Meta:
        model = OrganizationalLegalForm
        fields = (
            'directory_version',
            'code',
            'full',
            'short',
        )


class CompanyINNSerializer(serializers.ModelSerializer):
    organizational_legal_form = OrganizationalLegalFormSerializer(read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Company
        fields = (
            'id',
            'name',
            'address',
            'inn',
            'kpp',
            'ogrn',
            'okato',
            'oktmo',
            'okpo',
            'okogu',
            'okfs',
            'okved',
            'okved_type',
            'type_company',
            'organizational_legal_form',
            'status',
        )
        read_only_fields = (
            'id',
            'name',
            'kpp',
            'ogrn',
            'okato',
            'oktmo',
            'okpo',
            'okogu',
            'okfs',
            'okved',
            'okved_type',
            'type_company',
            'status',
        )


class CompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(required=False, allow_null=True,
                                                    write_only=True, queryset=Address.objects.all())
    logo = serializers.ImageField(read_only=True)
    logo_upload = serializers.CharField(write_only=True, required=False)
    organizational_legal_form = OrganizationalLegalFormSerializer(required=False, allow_null=True)

    class Meta:
        model = Company
        fields = (
            'id',
            'name',
            'short_name',
            'tagline',
            'address',
            'address_id',
            'slug',
            'description',
            'inn',
            'kpp',
            'ogrn',
            'okato',
            'oktmo',
            'okpo',
            'okogu',
            'okfs',
            'okved',
            'okved_type',
            'type_company',
            'organizational_legal_form',
            'status',
            'phone',
            'email',
            'logo',
            'logo_upload',
            'bank_details',
        )

    def create(self, validated_data):
        profile = self.context["profile"]
        logo_upload = validated_data.pop("logo_upload", None)
        address = validated_data.pop("address_id", None)
        organizational_legal_form = validated_data.pop("organizational_legal_form", None)
        bank_details = validated_data.pop("bank_details", None)

        if logo_upload is not None:
            try:
                _logo_file = get_img_from_data_url(logo_upload)[0]
            except Exception:
                raise serializers.ValidationError(_('Not valid media "image".'))

            validated_data["logo"] = _logo_file

        if address:
            validated_data["address"] = address

        if organizational_legal_form:
            organizational_legal_form_instance = OrganizationalLegalForm.objects.create(**organizational_legal_form)
            validated_data["organizational_legal_form"] = organizational_legal_form_instance

        if bank_details:
            bank = bank_details.pop("bank_id")
            bank_details.pop("id", None)
            validated_data["bank_details"] = BankDetails.objects.create(**bank_details, bank=bank)

        instance = Company.objects.create(**validated_data, profile=profile)

        profile.user_type = TypeUser.OWNER_COMPANY.value
        profile.save()

        return instance

    def update(self, instance, validated_data):
        logo_upload = validated_data.pop("logo_upload", None)
        address = validated_data.pop("address", None)
        organizational_legal_form = validated_data.pop("organizational_legal_form", None)
        bank_details = validated_data.pop("bank_details", None)

        address_instance = None
        bank_details_instance = None

        if logo_upload is not None:
            if instance.logo:
                instance.logo.delete()
            try:
                _logo_file = get_img_from_data_url(logo_upload)[0]
            except Exception:
                raise serializers.ValidationError(_('Not valid media "image".'))

            instance.logo = _logo_file

        if address:
            validated_data["address"] = address

        if organizational_legal_form:
            organizational_legal_form_instance = instance.organizational_legal_form
            if organizational_legal_form_instance:
                for (key, value) in organizational_legal_form.items():
                    setattr(organizational_legal_form_instance, key, value)

                organizational_legal_form_instance.save()

            else:
                organizational_legal_form_instance = OrganizationalLegalForm.objects.create(**organizational_legal_form)
                instance.organizational_legal_form = organizational_legal_form_instance

        if bank_details:
            bank = bank_details.pop("bank_id")
            bank_details_id = bank_details.pop("id", None)
            if bank_details_id:
                try:
                    bank_details_instance = BankDetails.objects.get(pk=bank_details_id)
                except BankDetails.DoesNotExist:
                    raise serializers.ValidationError(_('Bank details not found.'))
                for (key, value) in bank_details.items():
                    setattr(bank_details_instance, key, value)
                    bank_details_instance.save()
            else:
                bank_details_instance = BankDetails.objects.create(**bank_details, bank=bank)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.address = address_instance
        instance.bank_details = bank_details_instance

        instance.save()
        return instance





class RoleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Role
        fields = (
            'id',
            'name',
            'module_admin',
            'module_report',
            'module_manager',
            'module_services',
            'module_orders',
            'module_landing',
            'module_tasks',
            'company',
            'branch',
        )

    def create(self, validated_data):
        if validated_data.get("branch"):
            if validated_data.get("module_admin", PermissionEnum.READER.value) > PermissionEnum.READER.value:
                validated_data["module_admin"] = PermissionEnum.READER.value
            if validated_data.get("module_manager", PermissionEnum.READER.value) > PermissionEnum.READER.value:
                validated_data["module_manager"] = PermissionEnum.READER.value

        return Role.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("branch"):
            validated_data["module_admin"] = PermissionEnum.READER.value
            validated_data["module_manager"] = PermissionEnum.READER.value

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        data = super(RoleSerializer, self).to_representation(instance)

        data["branch"] = instance.branch.to_dict() if instance.branch else None

        return data


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=25)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'phone',
            'password',
        )

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("phone"):
            raise serializers.ValidationError(_("Password and email were not specified."))
        if attrs.get("email") and attrs.get("phone"):
            raise serializers.ValidationError(_("One field is required for registration:'email' or 'phone'"))
        return attrs


class ManagerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(write_only=True)
    profile = ProfileSerializer(required=False, allow_null=True)
    roles = RoleSerializer(many=True, read_only=True)
    role_pk = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all(), write_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    notification_settings = NotificationSettingsSerializer(required=False, allow_null=True)

    class Meta:
        model = Manager
        fields = (
            'id',
            'user',
            'profile',
            'roles',
            'role_pk',
            'company',
            'notification_settings',
        )

    def validate(self, attrs):
        role_pk = attrs.get("role_pk")
        user = attrs.get("user")

        if not self.instance and not attrs.get("user"):
            raise serializers.ValidationError(_("Password and email were not specified."))

        for _role in role_pk:
            if _role.company.pk != attrs.get("company").pk:
                raise serializers.ValidationError(_("Permission denied."))

        if not self.instance:
            registration_field = "email" if user.get("email") else "phone"
            try:
                User.objects.get(**{registration_field: user[registration_field]})
                raise serializers.ValidationError(_('User with this email address already exists.'))
            except User.DoesNotExist:
                pass

        return attrs

    def create(self, validated_data):
        roles = validated_data.pop("role_pk")
        user = validated_data.pop("user")
        profile_data = validated_data.pop("profile", None)
        notification_settings = validated_data.pop("notification_settings", None)

        if notification_settings:
            is_email = notification_settings.get("is_email", False)
            is_phone = notification_settings.get("is_phone", False)
            notification_settings_validated_data = {}

            if is_email is not Empty:
                notification_settings_validated_data["is_email"] = is_email

            if is_phone is not Empty:
                notification_settings_validated_data["is_phone"] = is_phone

            validated_data["notification_settings"] = NotificationSettings.objects.create(
                **notification_settings_validated_data
            )

        else:
            validated_data["notification_settings"] = NotificationSettings.objects.create()

        user_instance = User.objects.create_manager(**user)

        if profile_data:
            for field in ("first_name", "last_name", "patronymic"):
                setattr(user_instance.profile, field, profile_data.get(field))
        user_instance.profile.user_type = TypeUser.MANAGER.value
        user_instance.profile.save()

        instance = Manager.objects.create(**validated_data, profile=user_instance.profile)
        instance.roles.add(*roles)

        ALERTS["created_manager"].send_alert(
            user_instance.email,
            AlertType.EMAIL,
            company=validated_data["company"],
            login=user_instance.email,
            password=user["password"],
            action={"url": reverse('authentication:login')},
            settings=settings
        )

        return instance

    def update(self, instance, validated_data):
        new_roles = []
        roles = validated_data.get("role_pk")
        profile_data = validated_data.pop("profile", None)
        roles_db_map = {r.pk: True for r in instance.roles.all()}
        notification_settings = validated_data.pop("notification_settings", None)
        user = validated_data.pop("user", None)

        if len(roles) > 0:
            for _role in roles:
                if not roles_db_map.get(_role.id):
                    new_roles.append(_role)

        if len(new_roles) > 0 or len(new_roles) != len(roles_db_map):
            instance.roles.clear()
            instance.roles.add(*roles)

            ALERTS["add_to_role"].send_alert(
                instance.profile.user.email,
                AlertType.EMAIL,
                company=validated_data["company"],
                action={"url": reverse('authentication:login')},
                settings=settings
            )

        instance.profile.user.email = user.get("email")
        instance.profile.user.phone = user.get("phone")
        instance.profile.user.save()

        if notification_settings:
            is_email = notification_settings.get("is_email", Empty)
            is_phone = notification_settings.get("is_phone", Empty)

            if is_email is not Empty:
                instance.notification_settings.is_email = is_email

            if is_phone is not Empty:
                instance.notification_settings.is_phone = is_phone

            instance.notification_settings.save()

        if profile_data:
            for field in ("first_name", "last_name", "patronymic"):
                setattr(instance.profile, field, profile_data.get(field))
            instance.profile.save()

        instance.save()

        return instance

    def to_representation(self, instance):
        data = super(ManagerSerializer, self).to_representation(instance)
        data["user"] = UserSerializer(instance.profile.user).data
        return data


class PublicCompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    short_name = serializers.CharField(read_only=True)
    tagline = serializers.CharField(read_only=True)
    address = AddressSerializer(read_only=True)
    logo = serializers.ImageField(read_only=True)

    class Meta:
        model = Company
        fields = (
            'id',
            'name',
            'short_name',
            'tagline',
            'address',
            'slug',
            'logo',
        )


class PublicBranchSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    company = PublicCompanySerializer(read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Branch
        fields = (
            'id',
            'name',
            'address',
            'description',
            'phone',
            'email',
            'company',
        )
