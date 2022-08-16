from typing import Dict, Any, Union, Tuple

from asgiref.sync import sync_to_async

from geo_city.models import City, Country, Region, Street
from geo_city.serializers import StreetSerializer


async def street_serializer(address: Dict[str, Any]) -> Union[StreetSerializer, None]:
    country_name = address.get("data", {}).get("country")
    region_name = address.get("data", {}).get("region")
    city_name = address.get("data", {}).get("city")
    street_name = address.get("data", {}).get("street")
    street_type = address.get("data", {}).get("street_type")

    _street_instance = None

    streets = await sync_to_async(Street.objects.filter, thread_sensitive=False)(
        city__name=city_name,
        street=street_name,
        street_type=street_type,
    )

    if len(streets) > 0:
        _street_instance = streets[0]

    else:
        if region_name and city_name:
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

            if city_instance and street_name:
                _street_instance = await sync_to_async(Street.objects.create, thread_sensitive=False)(
                    city=city_instance, street=street_name, street_type=street_type)

    return StreetSerializer(_street_instance) if _street_instance else None
