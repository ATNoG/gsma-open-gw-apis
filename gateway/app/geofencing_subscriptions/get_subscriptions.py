from typing import Any, Iterable
from fastapi import APIRouter
from redis import Redis

from app.config import settings
from app.geofencing_subscriptions.schemas import Subscription
from app.redis import RedisDep


router = APIRouter()


def key2sub(key, redis: Redis) -> Subscription:
    sub = validate_get(redis.get(key))
    if sub is None:
        raise Exception("Type error: type of sub is not bytes")
    return Subscription.model_validate_json(sub)


def validate_get(res: Any) -> bytes | None:
    if isinstance(res, bytes):
        return res


def validate_keys(keys: Any) -> list[bytes] | None:
    if isinstance(keys, list) and all(isinstance(k, bytes) for k in keys):
        return keys


@router.get("/")
def get_subscriptions(redis: RedisDep) -> Iterable[Subscription]:
    keys = validate_keys(redis.keys(f"{settings.redis_geofencing_prefix}:*"))
    if keys is None:
        raise Exception("Type error: type of keys should be list[bytes]")

    return map(lambda k: key2sub(k, redis), keys)
