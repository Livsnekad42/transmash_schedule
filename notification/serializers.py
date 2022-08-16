from rest_framework import serializers

from notification.models import NotificationSettings


class NotificationSettingsSerializer(serializers.ModelSerializer):
    is_email = serializers.BooleanField(required=False)
    is_phone = serializers.BooleanField(required=False)

    class Meta:
        model = NotificationSettings
        fields = (
            'is_email',
            'is_phone',
        )
