import operator
from functools import reduce

from django.db.models import Q
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from authentication.models import User
from administration.services.constants import ADMIN_MODULES, PermissionAdmin
from core.serialize_fields.phone import PhoneField
from profiles.models import Profile, TypeUser


class ContentTypeSerializer(serializers.ModelSerializer):
    app_label = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=100)

    class Meta:
        model = ContentType
        fields = (
            'app_label',
            'model',
        )


class PermissionSerializer(serializers.ModelSerializer):
    module = serializers.CharField(max_length=255)
    codename = serializers.CharField(max_length=100)
    permission_type = serializers.CharField(max_length=255)

    class Meta:
        model = Permission
        fields = (
            'id',
            'module',
            'codename',
            'permission_type',
        )

    def validate(self, attrs):
        try:
            PermissionAdmin(attrs["codename"])
        except ValueError:
            raise serializers.ValidationError(_('Not valid "codename".'))

        module = list(filter(lambda x: x["name"] == attrs["module"], ADMIN_MODULES))
        if len(module) == 0:
            raise serializers.ValidationError(_('Not found module.'))

        return attrs

    def to_representation(self, instance):
        data = {
            "id": instance.pk,
        }

        find_module = list(filter(lambda m: m["model"].model_name() == instance.content_type.model, ADMIN_MODULES))

        if len(find_module) == 0:
            return data

        data["module"] = find_module[0]["title"]
        data["codename"] = instance.codename,
        data["permission_type"] = instance.codename.split("_")[0],

        return data


class PermissionModuleSerializer(serializers.Serializer):
    module = serializers.CharField(read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        fields = (
            'module',
            'permissions',
        )


class GroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=150)
    permission_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.filter(
        reduce(
            operator.or_,
            (Q(codename__contains=item["model"].model_name()) for item in ADMIN_MODULES)
        )
    ))
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'permission_ids',
            'permissions',
        )

    def create(self, validated_data):
        group = Group.objects.create(name=validated_data["name"])
        group.permissions.add(*validated_data["permission_ids"])

        return group

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.permissions.clear()
        instance.permissions.add(*validated_data["permission_ids"])

        instance.save()

        return instance

    def to_representation(self, instance):
        data = {
            "id": instance.pk,
            "name": instance.name,
        }
        permissions = []
        permission_ids = []

        for _perm in instance.permissions.all():
            find_module = list(filter(lambda m: m["model"].model_name() == _perm.content_type.model, ADMIN_MODULES))

            if len(find_module) > 0:
                module = find_module[0]["title"]
            else:
                continue

            permission_ids.append(_perm.pk)
            permissions.append({
                "module": module,
                "codename": _perm.codename,
                "permission_type": _perm.codename.split("_")[0],
            })

        data["permission_ids"] = permission_ids
        data["permissions"] = permissions

        return data


class AdminUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_null=True)
    phone = PhoneField(required=False, allow_null=True, max_length=25, min_length=10)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    groups_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Group.objects.all(), write_only=True)
    is_superuser = serializers.BooleanField(default=False)

    class Meta:
        fields = (
            'email',
            'phone',
            'password',
            'groups',
            'groups_ids',
            'is_superuser',
        )

    def validate(self, attrs):
        if not attrs.get("password"):
            raise serializers.ValidationError(_('Required field "password".'))

        if not attrs.get("email") and not attrs.get("phone"):
            raise serializers.ValidationError(_('Required field "email" or "phone".'))

        return attrs


class AdminProfileSerializer(serializers.ModelSerializer):
    user = AdminUserSerializer()

    class Meta:
        model = Profile
        fields = (
            'user',
            'first_name',
            'last_name',
            'patronymic',
        )

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        groups = user_data.pop("groups_ids", [])

        try:
            user_instance = User.objects.create_manager(**user_data)
        except IntegrityError:
            raise serializers.ValidationError(_(f'User already exists.'))

        if len(groups) > 0:
            user_instance.groups.add(*groups)

        for (key, value) in validated_data.items():
            setattr(user_instance.profile, key, value)

        user_instance.profile.save()

        return user_instance.profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        groups = user_data.pop("groups_ids", None)

        if user_data.get("email"):
            instance.user.email = user_data["email"]

        if user_data.get("phone"):
            instance.user.email = user_data["phone"]

        if groups is not None:
            instance.user.groups.clear()

        if len(groups) > 0:
            instance.user.groups.add(*groups)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.user.save()
        instance.save()

        return instance
