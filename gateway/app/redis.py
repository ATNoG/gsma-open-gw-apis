from fastapi import Depends

from typing import Annotated
import redis.asyncio as redis

from app.settings import settings

# This function isn't typed
# mypy: ignore-errors
_client: redis.Redis = redis.from_url(
    settings.redis_url, encoding="utf-8", decode_responses=True
)


def get_redis() -> redis.Redis:
    return _client


RedisDep = Annotated[redis.Redis, Depends(get_redis)]
