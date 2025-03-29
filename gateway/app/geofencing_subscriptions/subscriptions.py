from datetime import datetime
from re import sub
from fastapi import APIRouter, HTTPException, Request, status
from http import HTTPStatus
from pydantic import AnyUrl
import requests
import geopy
import logging
from redis import Redis

r = Redis()


from app.geofencing_subscriptions.schemas import (
    MonitoringEventSubscription,
    MonitoringEventSubscriptionCreate,
    MonitoringType,
    Protocol,
    Status,
    Subscription,
    SubscriptionRequest,
)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

router = APIRouter(prefix="/geofencing-subscriptions/v0.4rc1")


@router.post("/subscription-webhook")
async def webhook(req: Request):
    print(await req.body())
    r.get()


@router.get("/subscriptions")
def get_subscritpions() -> None:
    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)


tempAuth = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDM1MjU5MDAsInN1YiI6IjEifQ.5MUBdijHFsKCqHnS5FyGNWBJTLx4-v1OKqorya--Fh8"
path = "/nef/api/v1/3gpp-monitoring-event/v1/camara/subscriptions"
baseUrl = "http://localhost:8888"


@router.post("/subscriptions")
def post_subscriptions(req: SubscriptionRequest) -> Subscription:
    body = MonitoringEventSubscriptionCreate(
        externalId="69001@domain.com",
        notificationDestination=AnyUrl(
            "http://host.docker.internal:8000/geofencing-subscriptions/v0.4rc1/subscription-webhook"
        ),
        monitoringType=MonitoringType.LOCATION_REPORTING,
        maximumNumberOfReports=30,
        monitorExpireTime=datetime.fromtimestamp(2_000_000_000),
    )
    res = requests.post(
        f"{baseUrl}{path}",
        data=body.model_dump_json(),
        headers={"Authorization": tempAuth},
    )
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

    r.set(f"geofencing_sub:{sub_id}", req.sink)

    return Subscription(
        protocol=Protocol.HTTP,
        sink=req.sink,
        types=req.types,
        config=req.config,
        startsAt=datetime.now(),
        id=sub_id,
        expiresAt=subscription.monitorExpireTime,
        status=Status.ACTIVE,
    )


@router.get("/subscriptions/{subscription_id}")
def get_subscritpion_by_id(subscription_id: int) -> None:
    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)


@router.delete("/subscriptions/{subscription_id}")
def delete_subscritpion_by_id(subscription_id: int) -> None:
    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)
