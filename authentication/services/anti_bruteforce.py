import enum
from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Tuple, NewType

from django.conf import settings

from core.app_services.redis_service import REDIS_SERVICE

BAN_TIME = getattr(settings, "BAN_TIME", timedelta(minutes=30))
COUNT_FAILED_ATTEMPT = getattr(settings, "COUNT_FAILED_ATTEMPT", 10)


USER_ID = NewType("USER_ID", str)
MESSAGE = NewType("MESSAGE", str)


class ResultStatus(enum.Enum):
    ERROR = "error"
    SUCCESS = "success"
    FAILURE = "failure"
    BAN = "ban"


@dataclass
class ResultCallFunc:
    status: ResultStatus
    result: str


class AntiBruteForce:
    """
    Decorator for tracking account hacking
    attempts by brute force passwords or verification codes
    """
    def __init__(self, key: str, max_count_fail: int = COUNT_FAILED_ATTEMPT, exp: int = BAN_TIME.seconds):
        self.key = f"{key}__anti_bruteforce"
        self.max_count_fail = max_count_fail
        self.exp = exp

    def check(self, user_id: USER_ID = False) -> Tuple[bool, ResultStatus]:
        if user_id:
            self.key = f"{user_id}_{self.key}"

        if self.is_banned():
            return False, ResultStatus.BAN

        self.increment_attempt()
        return True, ResultStatus.SUCCESS

    def __call__(self, func: Callable[[USER_ID, ...],  Tuple[bool, MESSAGE]]) -> \
            Callable[[USER_ID, ...], Tuple[bool, ResultCallFunc]]:
        def wrapper(user_id: USER_ID, *args, **kwargs) -> Tuple[bool, ResultCallFunc]:
            self.key = f"{user_id}_{self.key}"
            if self.is_banned():
                return False, ResultCallFunc(ResultStatus.BAN, "")

            try:
                result, message = func(user_id, *args, **kwargs)

            except Exception as e:
                return False, ResultCallFunc(ResultStatus.ERROR, str(e))

            if not result:
                self.increment_attempt()
                return False, ResultCallFunc(ResultStatus.FAILURE, message)

            return True, ResultCallFunc(ResultStatus.SUCCESS, message)

        return wrapper

    def increment_attempt(self):
        data_fail = REDIS_SERVICE.get_data(self.key)
        if not data_fail:
            _data_fail = {"count": 0}
            REDIS_SERVICE.set_data(self.key, _data_fail, self.exp)

        else:
            _data_fail = {"count": data_fail.get("count", 0) + 1}
            REDIS_SERVICE.set_data(self.key, _data_fail, self.exp)

    def is_banned(self) -> bool:
        data_fail = REDIS_SERVICE.get_data(self.key)
        if data_fail and data_fail.get("count") >= self.max_count_fail:
            return True

        return False




