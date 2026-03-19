import json
from typing import Any
import redis.asyncio as redis
from conf.settings import settings

redis_client = redis.from_url(
    settings.redis_url,
    decode_response=True
)


async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(e)
        return None


async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(e)
        return None


async def set_cache(key: str, value: Any, expire: int = 1200):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
            await redis_client.setex(key, expire, value)
            return True
    except Exception as e:
        print(e)
        return False
