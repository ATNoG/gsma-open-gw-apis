from http import HTTPStatus
from typing import Any
from fastapi import APIRouter

from app.config import settings
from app.exceptions import ApiException
from app.geofencing_subscriptions.schemas import Subscription
from app.redis import RedisDep


router = APIRouter()


def validate_get(res: Any) -> bytes | None:
    if isinstance(res, bytes):
        return res


@router.get("/{subscriptionId}")
def get_subscriptions_by_id(subscriptionId: str, redis: RedisDep) -> Subscription:
    val = redis.get(f"{settings.redis_geofencing_prefix}:{subscriptionId}")
    if val is None:
        raise ApiException(
            HTTPStatus.NOT_FOUND,
            "NOT_FOUND",
            "The specified resource is not found.",
        )

    sub = validate_get(val)
    if sub is None:
        raise Exception("Type error: type of sub should be bytes")

    return Subscription.model_validate_json(sub)
