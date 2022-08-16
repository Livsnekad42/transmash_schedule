from typing import Dict, Union, List, Tuple, Any

from core.app_services.dadata import find_city_address, Point, find_place
from geo_city.services.data_converters.place import place_serializer


async def get_valid_street(city_name: str, street: str, *address) -> Union[List[Dict], None]:
    resp = await find_city_address(city_name, f"{street} {address}" if " ".join(address) else street)

    if not resp.is_success:
        return None

    resp_data = resp.json()

    if not resp_data.get("suggestions") or len(resp_data["suggestions"]) == 0:
        return None

    data = []

    if address:
        houses = set()
        for street_data in resp_data["suggestions"]:
            if street_data.get("data", {}).get("house") and street_data["data"]["house"] not in houses:
                data.append(street_data)
                houses.add(street_data["data"]["house"])

    else:
        streets = set()
        for street_data in resp_data["suggestions"]:
            if street_data.get("data", {}).get("street") and street_data["data"]["street"] not in streets:
                data.append(street_data)
                streets.add(street_data["data"]["street"])

    return data


async def get_place_from_gps(gps: Point) -> Union[Dict[str, Any], None]:
    resp = await find_place(gps)

    if not resp.is_success:
        return None

    resp_data = resp.json()

    if len(resp_data["suggestions"]) == 0:
        return None

    address = resp_data["suggestions"][0]

    return await place_serializer(address, gps)

