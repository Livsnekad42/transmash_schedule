from typing import Union, Dict

from core.app_services.dadata import find_by_inn
from geo_city.services.data_converters.address import address_serializer


async def get_company_data_from_inn(inn: str) -> Union[Dict, None]:
    resp = await find_by_inn(inn)
    if not resp.is_success:
        return None

    resp_data = resp.json()

    if not resp_data.get("suggestions") or len(resp_data["suggestions"]) == 0:
        return None

    data = resp_data["suggestions"][0].get("data", None)

    if not data:
        return None

    valid_data = {
        "address": None,
        "organizational_legal_form": None,
    }

    address = data.get("address")
    organizational_legal_form = data.get("opf")

    if address:
        _address_serializer = await address_serializer(address)
        valid_data["address"] = _address_serializer.data if _address_serializer else None

    if organizational_legal_form:
        valid_data["organizational_legal_form"] = {}
        valid_data["organizational_legal_form"]["directory_version"] = organizational_legal_form["type"]
        valid_data["organizational_legal_form"]["code"] = organizational_legal_form["code"]
        valid_data["organizational_legal_form"]["full"] = organizational_legal_form["full"]
        valid_data["organizational_legal_form"]["short"] = organizational_legal_form["short"]

    valid_data["kpp"] = data.get("kpp")
    valid_data["inn"] = data.get("inn")
    valid_data["ogrn"] = data.get("ogrn")
    valid_data["okpo"] = data.get("okpo")
    valid_data["okato"] = data.get("okato")
    valid_data["oktmo"] = data.get("oktmo")
    valid_data["okogu"] = data.get("okogu")
    valid_data["okfs"] = data.get("okfs")
    valid_data["okved"] = data.get("okved")
    valid_data["okveds"] = data.get("okveds")
    valid_data["okved_type"] = data.get("okved_type")
    valid_data["type_company"] = data.get("type")
    valid_data["name"] = data.get("name", {}).get("full_with_opf")

    return valid_data
