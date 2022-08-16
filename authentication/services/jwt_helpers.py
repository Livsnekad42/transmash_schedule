from typing import Union, Dict
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from rest_framework_jwt.settings import api_settings

# import rest_framework_jwt.utils.jwt_payload_handler
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


def create_token(user) -> str:
    return jwt_encode_handler(jwt_payload_handler(user))


def create_token_from_dict(data: dict, seconds: int = 0) -> str:
    if seconds:
        date = datetime.today() + timedelta(seconds=seconds)
        data["expires"] = int(date.timestamp())

    encoded_token = jwt.encode(data, settings.SECRET_KEY, algorithm='HS256')
    return encoded_token.decode()


def decode_token2dict(token: str) -> Union[dict, None]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithm='HS256')
        if payload.get("expires"):
            try:
                date = datetime.fromtimestamp(payload["expires"])
            except (ValueError, TypeError):
                return None

            if date < datetime.today():
                return None
    except jwt.exceptions.InvalidSignatureError:
        payload = None

    return payload
