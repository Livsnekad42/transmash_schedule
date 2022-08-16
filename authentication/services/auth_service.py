import random
from datetime import timedelta, datetime
from typing import Union, Tuple, Dict, Callable

from authentication.services.anti_bruteforce import AntiBruteForce
from core.app_services.redis_service import REDIS_SERVICE


KEY_COUNT_FAILED = "{0}_failed"


def create_randoms(length: int = 4) -> str:
    return ''.join(map(str, random.sample(range(length * 10), length)))[:length]


def create_code() -> str:
    return create_randoms(random.randrange(4, 6))


def create_duo_code() -> Tuple[str, str]:
    prefix = create_randoms(random.randrange(4, 6))
    suffix = create_randoms(random.randrange(50, 80))
    return prefix, suffix


def set_verify_code_from_redis(user_id: int, exp: int, length: int = 5) -> str:
    code = create_randoms(length)
    REDIS_SERVICE.set_data(f"{user_id}_{code}", {"id": user_id}, exp)
    return code


@AntiBruteForce("validate_code")
def is_valid_code(user_id: int, code: str) -> Tuple[bool, str]:
    key = f"{user_id}_{code}"
    user_data = REDIS_SERVICE.get_data(key)
    if not user_data:
        return False, "not found"

    if user_data.get("id") == user_id:
        REDIS_SERVICE.delete(key)
        return True, ""

    return False, "error format"


def set_verify_duo_code_from_redis(user_id: int, exp: int) -> Tuple[str, str]:
    prefix, suffix = create_duo_code()

    REDIS_SERVICE.set_data(f"{prefix}_{suffix}", {"id": user_id}, exp)
    return prefix, suffix


def is_valid_duo_code(prefix: str, suffix: str) -> Union[int, None]:
    user_data = REDIS_SERVICE.get_data(f"{prefix}_{suffix}")
    if not user_data:
        return None

    REDIS_SERVICE.delete(f"{prefix}_{suffix}")
    return user_data.get("id")


def is_live_phone_code(user_id: int, created_at: datetime, exp_time: timedelta) -> bool:
    if created_at.replace(tzinfo=None) + exp_time < datetime.today():
        return False

    return True


def verify_refresh_phone_code(created_at: datetime, exp_time: timedelta) -> int:
    t = created_at.replace(tzinfo=None) + exp_time
    if t > datetime.today():
        return (t - datetime.today()).seconds

    return -1


def set_restore_password_code_from_redis(user_id: int, exp: int) -> str:
    code = create_randoms(random.randrange(8, 10))
    REDIS_SERVICE.set_data(code, {"id": user_id}, exp)
    return code


def get_count_failed_confirm_user(user_id: int) -> int:
    key = KEY_COUNT_FAILED.format(user_id)
    user_data = REDIS_SERVICE.get_data(key)
    if not user_data:
        return 0

    return user_data.get("number_attempts")


def increment_count_failed_confirm_user(user_id: int, exp: int) -> int:
    key = KEY_COUNT_FAILED.format(user_id)
    user_data = REDIS_SERVICE.get_data(key)
    if not user_data:
        REDIS_SERVICE.set_data(key, {"number_attempts": 1}, exp)

    REDIS_SERVICE.set_data(key, {"number_attempts": user_data.get("number_attempts", 0) + 1}, exp)


def set_exp_to_key(key: str, exp: int):
    data = REDIS_SERVICE.get_data(key)
    if data:
        REDIS_SERVICE.set_data(key, data, exp)

