from rest_framework import serializers

from administration.models import Partner
from core.serialize_fields.phone import PhoneField
from geo_city.serializers import AddressSerializer


class PartnerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=150, required=False, allow_null=True)
    short_name = serializers.CharField(max_length=50, required=False, allow_null=True)
    phone = PhoneField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    address = AddressSerializer(read_only=True)
    address_id = AddressSerializer(write_only=True)

    class Meta:
        model = Partner
        fields = (
            'id',
            'name',
            'short_name',
            'phone',
            'email',
            'address',
            'address_id',
        )

    def create(self, validated_data):
        address = validated_data.pop("address_id", None)
        validated_data["address"] = address

        return Partner.objects.create(**validated_data)

    def update(self, instance, validated_data):
        address = validated_data.pop("address_id", None)
        validated_data["address"] = address

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance