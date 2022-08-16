from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from authentication.models import User
from core.converters.images import get_img_from_data_url
from core.mixins.valid_user_password import ValidUserPasswordMixin
from core.serialize_fields.img import ImgBase64Field
from .models import Profile, Archive


class RefreshPasswordSerializer(serializers.ModelSerializer, ValidUserPasswordMixin):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    new_password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = (
            'password',
            'new_password',
        )

    def validate(self, attrs):
        password = attrs.get("password")
        new_password = attrs.get("new_password")

        if not new_password or not password:
            raise serializers.ValidationError(_('Password and new_password required fields.'))

        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password', None)

        instance.set_password(new_password)
        instance.save()

        return instance


class RefreshEmailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    email = serializers.EmailField(write_only=True)
    new_email = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = (
            'password',
            'new_email',
            'email',
        )

    def validate(self, attrs):
        password = attrs.get("password")
        if not password:
            raise serializers.ValidationError(_('Password and new password required fields.'))

        if not self.instance.check_password(password):
            raise serializers.ValidationError(_('Invalid password.'))

        return attrs

    def update(self, instance, validated_data):
        new_email = validated_data.pop('new_email', None)

        instance.email = new_email
        instance.save()

        return instance


class ArchiveSerializer(serializers.ModelSerializer):
    file = serializers.FileField(read_only=True)

    class Meta:
        model = Archive
        fields = (
            'file',
            'created_at',
            'updated_at',
        )


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    last_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    patronymic = serializers.CharField(max_length=255, required=False, allow_null=True)
    avatar = serializers.ImageField(read_only=True)
    avatar_thumb = serializers.ImageField(read_only=True)
    date_birth = serializers.DateField(required=False, allow_null=True)
    user_type = serializers.CharField(read_only=True)
    avatar_upload = ImgBase64Field(required=False, write_only=True, allow_null=True)
    archives = ArchiveSerializer(many=True, read_only=True)
    background_tree = serializers.CharField(required=False, allow_null=True)
    
    class Meta:
        model = Profile
        fields = (
            'first_name',
            'last_name',
            'patronymic',
            'avatar',
            'avatar_thumb',
            'date_birth',
            'user_type',
            'avatar_upload',
            'archives',
            'background_tree',
        )

    def update(self, instance, validated_data):
        avatar_upload = validated_data.pop("avatar_upload", None)
        avatar_file = None

        if avatar_upload is not None:
            if instance.avatar:
                instance.avatar.delete()
                instance.avatar_thumb.delete()

            if avatar_upload:
                avatar_file = get_img_from_data_url(avatar_upload)[0]
                instance.avatar = avatar_file

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save(new_avatar=bool(avatar_file))
        return instance
