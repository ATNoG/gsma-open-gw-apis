from typing import Annotated
from fastapi import Depends
from redis import Redis


redis = Redis()


async def get_redis() -> Redis:
    return redis


RedisDep = Annotated[Redis, Depends(get_redis)]