from http import HTTPStatus
from typing import Any
from fastapi import APIRouter
from fastapi.responses import Response
import requests

from app.config import settings
from app.exceptions import ApiException
from app.redis import RedisDep


router = APIRouter()

path = "/nef/api/v1/3gpp-monitoring-event/v1/camara/subscriptions"
tempAuth = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQyMjQ4MzYsInN1YiI6IjEifQ.-POD0O20f6fe720oGdYKs9AbwhW7KbF5GQ-Sc_nUyug"


def validate_get(res: Any) -> bytes | None:
    if isinstance(res, bytes):
        return res


@router.delete("/{subscriptionId}")
def delete_subscriptions_by_id(subscriptionId: str, redis: RedisDep) -> Response:
    val = redis.delete(f"{settings.redis_geofencing_prefix}:{subscriptionId}")
    if val is None:
        raise ApiException(
            HTTPStatus.NOT_FOUND,
            "NOT_FOUND",
            "The specified resource is not found.",
        )

    requests.delete(
        f"{settings.NEF_HOST}{path}/{subscriptionId}",
        headers={"Authorization": tempAuth},
    )

    return Response(status_code=HTTPStatus.NO_CONTENT)
