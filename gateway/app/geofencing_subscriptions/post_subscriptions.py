from datetime import datetime
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import AnyUrl, RootModel
import requests
from app.geofencing_subscriptions.schemas import (
    MonitoringEventSubscription,
    MonitoringEventSubscriptionCreate,
    MonitoringType,
    Protocol,
    Status,
    Subscription,
    SubscriptionRequest,
)
from app.exceptions import ApiException
from app.redis import RedisDep
from app.config import settings

router = APIRouter()

path = "/nef/api/v1/3gpp-monitoring-event/v1/camara/subscriptions"
tempAuth = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQyMjQ4MzYsInN1YiI6IjEifQ.-POD0O20f6fe720oGdYKs9AbwhW7KbF5GQ-Sc_nUyug"


def get_root(val: Optional[RootModel]):
    return val and val.root


_webhook_url = AnyUrl("http://host.docker.internal:8000/geofencing-webhook")


@router.post("/subscriptions")
def post_subscriptions(req: SubscriptionRequest, redis: RedisDep) -> Subscription:
    if req.protocol != Protocol.HTTP:
        raise ApiException(
            status=HTTPStatus.BAD_REQUEST,
            code="INVALID_PROTOCOL",
            message="Only HTTP is supported.",
        )

    device = req.config.subscriptionDetail.device
    body = MonitoringEventSubscriptionCreate(
        externalId=get_root(device.networkAccessIdentifier),
        notificationDestination=_webhook_url,
        monitoringType=MonitoringType.LOCATION_REPORTING,
        maximumNumberOfReports=30,
        monitorExpireTime=req.config.subscriptionExpireTime,
    )
    res = requests.post(
        f"{settings.NEF_HOST}{path}",
        data=body.model_dump_json(),
        headers={"Authorization": tempAuth},
    )
    if res.status_code != HTTPStatus.CREATED.value:
        raise HTTPException(status_code=res.status_code, detail=res.content)

    subscription = MonitoringEventSubscription.model_validate_json(res.content)

    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    if subscription.link is None or subscription.link.path is None:
        raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)

    subscription_path = subscription.link.path
    sub_id = subscription_path.rsplit("/")[-1]

    res = Subscription(
        protocol=Protocol.HTTP,
        sink=req.sink,
        types=req.types,
        config=req.config,
        startsAt=datetime.now(),
        id=sub_id,
        expiresAt=subscription.monitorExpireTime,
        status=Status.ACTIVE,
    )

    redis.set(f"{settings.redis_geofencing_prefix}:{sub_id}", res.model_dump_json())

    return res
