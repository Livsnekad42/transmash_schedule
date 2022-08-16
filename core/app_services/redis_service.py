import json
from typing import Dict, Union

import redis


class RedisService:
    def __init__(self):
        self.r = None
        self.connect()

    def set_data(self, key: str, data: Dict, exp: int = -1):
        _json = json.dumps(data)
        r = self.get_redis()
        r.set(key, _json, exp)

    def get_data(self, key: str) -> Union[Dict, None]:
        r = self.get_redis()
        _json = r.get(key)
        if not _json:
            return None

        return json.loads(_json)

    def connect(self):
        self.r = redis.Redis(db=1)

    def get_redis(self) -> redis.Redis:
        if self.r.ping():
            return self.r

        self.connect()
        return self.r

    def delete(self, key):
        r = self.get_redis()
        r.delete(key)


REDIS_SERVICE = RedisService()
