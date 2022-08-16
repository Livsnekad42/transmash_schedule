from typing import Dict, Any

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from geo_city.models import Region, City, Country, Street, Place, Address


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('code', 'name')


class RegionSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Region
        fields = (
            'country',
            'name',
            'federal_district',
            'region_iso_code',
            'region_type_full',
            'region_iso_code',
        )


class CitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    region = RegionSerializer(read_only=True)
    name = serializers.CharField(read_only=True)
    timezone = serializers.CharField(read_only=True)
    latitude = serializers.DecimalField(read_only=True, max_digits=21, decimal_places=18)
    longitude = serializers.DecimalField(read_only=True, max_digits=21, decimal_places=18)

    class Meta:
        model = City
        fields = ('id', 'region', 'name', 'latitude', 'longitude', 'timezone')

    def validate(self, attrs):
        if attrs.get("id"):
            return attrs

        if not attrs.get("name"):
            raise serializers.ValidationError(_('Must include "name".'))

        return attrs

    def create(self, validated_data):
        city = City.objects.create(**validated_data)
        return city


class StreetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    street_type = serializers.CharField(required=False, max_length=10)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), write_only=True,
                                                 required=True, allow_null=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = Street
        fields = ('id', 'city_id', 'city', 'street_type', 'street')

    def validate(self, attrs):
        city_id = attrs.get("city_id")
        instance_id = attrs.get("id")

        if not instance_id and not city_id:
            raise serializers.ValidationError(_('Must include "city_id".'))

        return attrs

    def create(self, validated_data):
        city = validated_data.pop("city_id", None)

        instance = Street.objects.create(
            street=validated_data["street"],
            street_type=validated_data.get("street_type", "ул"),
            city=city
        )
        return instance

    def update(self, instance, validated_data):
        instance.street_type = validated_data["street_type"]
        instance.street = validated_data["street"]
        instance.save()
        return instance


class PlaceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), write_only=True,
                                                 required=False, allow_null=True)
    city = CitySerializer(read_only=True)
    place_name = serializers.CharField(max_length=250, required=False, allow_null=True)
    latitude = serializers.DecimalField(required=False, allow_null=True, max_digits=21, decimal_places=18)
    longitude = serializers.DecimalField(required=False, allow_null=True, max_digits=21, decimal_places=18)

    class Meta:
        model = Place
        fields = (
            'id',
            'city_id',
            'city',
            'place_name',
            'latitude',
            'longitude',
        )

    def validate(self, attrs):
        instance_id = attrs.get("id")
        if instance_id and not self.instance:
            try:
                self.instance = Place.objects.get(pk=instance_id)

            except Place.DoesNotExist:
                raise serializers.ValidationError(_('Must include "building".'))

        if attrs.get("city_id"):
            attrs["city"] = attrs["city_id"]
            attrs["city_id"] = attrs["city_id"].pk

        return attrs

    def create(self, validated_data):
        # city = validated_data.pop("city_id", None)
        # validated_data["city"] = city

        place = Place.objects.create(**validated_data)
        return place

    def update(self, instance, validated_data):
        validated_data.pop("id", None)
        # city = validated_data.pop("city_id", None)
        # validated_data["city"] = city

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class AddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    street_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Street.objects.all())
    street = StreetSerializer(read_only=True)
    home = serializers.CharField(required=False, max_length=10)
    description = serializers.CharField(required=False, max_length=100)
    district = serializers.CharField(required=False, max_length=150)
    latitude = serializers.DecimalField(required=False, max_digits=21, decimal_places=18)
    longitude = serializers.DecimalField(required=False, max_digits=21, decimal_places=18)

    class Meta:
        model = Address
        fields = ('id', 'district', 'street_id', 'street', 'home', 'description', 'latitude', 'longitude')

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        street = validated_data.pop("street_id", None)
        validated_data["street"] = street
        return AddressSerializer.update_or_create(validated_data)

    def update(self, instance, validated_data):
        street = validated_data.pop("street_id", None)
        validated_data["street"] = street
        return AddressSerializer.update_or_create(validated_data, instance)

    @staticmethod
    def update_or_create(validated_data: Dict[str, Any], instance: Address = None) -> Address:
        _id = validated_data.pop("id", None)

        if _id and not instance:
            try:
                instance = Address.objects.get(pk=_id)
            except Address.DoesNotExist:
                raise serializers.ValidationError(_("Address not found."))

        # if street and street.get("id"):
        #     try:
        #         street_instance = Street.objects.get(pk=street["id"])
        #     except Street.DoesNotExist:
        #         raise serializers.ValidationError(_("Street not found."))
        #
        # else:
        #     street_instance = None
        #
        # if street:
        #     street_serializer = StreetSerializer(street_instance, data=street)
        #     street_serializer.is_valid(raise_exception=True)
        #     street_instance = street_serializer.save()

        if not instance:
            instance = Address.objects.create(**validated_data)
            return instance

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        # instance.street = street_instance
        instance.save()

        return instance


class SearchStreetSerializer(serializers.Serializer):
    street_type = serializers.CharField()
    street = serializers.CharField()

    class Meta:
        fields = (
            'street',
            'street_type',
        )


class SearchStreetListSerializer(serializers.Serializer):
    city_name = serializers.CharField(write_only=True, required=True)
    street = serializers.CharField(write_only=True, required=True)
    streets = StreetSerializer(many=True, read_only=True)

    class Meta:
        fields = (
            'city_name',
            'street',
            'streets',
        )


class SearchAddressListSerializer(serializers.Serializer):
    city_name = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(write_only=True, required=True)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        fields = (
            'city_name',
            'address',
            'addresses',
        )


class ReverseGeocodingSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=True, write_only=True)
    lng = serializers.FloatField(required=True, write_only=True)
    place = PlaceSerializer(read_only=True)

    class Meta:
        fields = (
            'lat',
            'lng',
            'place',
        )
