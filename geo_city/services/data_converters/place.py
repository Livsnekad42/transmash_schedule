from typing import Dict, Any, Union

from asgiref.sync import sync_to_async

from core.app_services.dadata import Point
from geo_city.models import City, Country, Region, Street


async def place_serializer(address: Dict[str, Any], gps: Point = None) -> Union[Dict[str, Any], None]:
    from geo_city.serializers import StreetSerializer, CitySerializer

    country_name = address.get("data", {}).get("country")
    region_name = address.get("data", {}).get("region")
    city_name = address.get("data", {}).get("city")
    street_name = address.get("data", {}).get("street")
    house = address.get("data", {}).get("house")

    if region_name and city_name:
        city_instance = None
        try:
            city_instance = await sync_to_async(City.objects.get, thread_sensitive=False)(
                region__name=region_name, name=city_name)
        except City.DoesNotExist:
            country_instance, _ = await sync_to_async(Country.objects.get_or_create, thread_sensitive=False)(
                name=country_name.capitalize(), defaults={
                    "code": address.get("data", {}).get("country_iso_code")
                }
            )
            region_instance, _ = await sync_to_async(Region.objects.get_or_create, thread_sensitive=False)(
                name=region_name,
                country=country_instance,
                defaults={
                    "region_kladr_id": address.get("data", {}).get("region_kladr_id"),
                    "region_iso_code": address.get("data", {}).get("region_iso_code"),
                    "region_type_full": address.get("data", {}).get("region_type_full"),
                    "federal_district": address.get("data", {}).get("federal_district"),
                }
            )
            city_instance = await sync_to_async(City.objects.create, thread_sensitive=False)(
                region=region_instance, name=city_name)
        if city_instance:
            street_instance = None

            if street_name:
                street_type = address.get("data", {}).get("street_type")
                if not street_type:
                    street_type = "ул"

                street_instance, _ = await sync_to_async(Street.objects.get_or_create, thread_sensitive=False)(
                    city=city_instance, street=street_name, street_type=street_type)

            return {
                "street": StreetSerializer(street_instance).data if street_instance else None,
                "city": CitySerializer(city_instance).data,
                "place_name": None,
                "building": house,
                "lat": gps.lat if gps else address.get("data", {}).get("geo_lat"),
                "lng": gps.lon if gps else address.get("data", {}).get("geo_lon"),
            }

    return None
