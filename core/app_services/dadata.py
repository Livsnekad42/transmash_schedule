from dataclasses import dataclass, asdict

from django.conf import settings

from core.base_api import REQUEST


@dataclass
class Point:
    lat: float
    lon: float
    radius_meters: float = 50


async def find_by_inn(inn: str):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
    token = settings.DADATA_API_KEY

    data = await REQUEST.arequest_post(url, headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {token}"
    }, json={
        "query": inn,
        "branch_type": "MAIN",
    })

    return data


async def find_city_address(city_name: str, street: str):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
    token = settings.DADATA_API_KEY
    secret = settings.DADATA_SECRET

    data = await REQUEST.arequest_post(url, headers={
        "Content-Type": "application/json",
        'Authorization': f"Token {token}",
        'X-Secret': secret,
    }, json={
        "query": f"{city_name} {street}"
    })

    return data


async def find_place(gps: Point):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address"
    token = settings.DADATA_API_KEY
    secret = settings.DADATA_SECRET

    data = await REQUEST.arequest_post(url, headers={
        "Content-Type": "application/json",
        'Authorization': f"Token {token}",
        'X-Secret': secret,
    }, json=asdict(gps))

    return data


async def find_bank(query: str):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/bank"
    token = settings.DADATA_API_KEY
    secret = settings.DADATA_SECRET

    data = await REQUEST.arequest_post(url, headers={
        "Content-Type": "application/json",
        'Authorization': f"Token {token}",
        'X-Secret': secret,
    }, json={
        "query": query
    })

    return data
