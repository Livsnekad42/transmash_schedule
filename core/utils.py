import random
import string
from datetime import timedelta
from typing import Union

from django.db import models

DEFAULT_CHAR_STRING = string.ascii_lowercase + string.digits


def generate_random_string(chars=DEFAULT_CHAR_STRING, size=6):
    return ''.join(random.choice(chars) for _ in range(size))


def convert_timedelta_to_str(t: timedelta) -> str:
    if t.seconds < 3600:
        return ":".join(str(t).split(":")[1:])

    return str(t)


def get_profile_in_request(request) -> Union[models.Model, None]:
    profile = getattr(request.user, "profile", None)
    return profile


def calc_value_minus_percent(value: Union[int, float], percent: Union[int, float]) -> float:
    return value - (value * percent / 100)
