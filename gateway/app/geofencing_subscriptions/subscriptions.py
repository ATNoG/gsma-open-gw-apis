from datetime import datetime
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from pydantic import AnyUrl
import requests
import geopy
import logging
from redis import Redis

from app.geofencing_subscriptions import router

from app.geofencing_subscriptions.schemas import (
    Area,
    AreaLeft,
    AreaType,
    CloudEvent,
    DateTime,
    Device,
    MonitoringNotification,
    NetworkAccessIdentifier,
    NotificationEventType,
    Source,
    SubscriptionId,
)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


@router.post("/subscription-webhook")
def webhook(notification: MonitoringNotification):
    if notification.subscription is None or notification.subscription.path is None:
        raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail="hi")

    subscription_path = notification.subscription.path
    sub_id = subscription_path.rsplit("/")[-1]

    sink = r.get(f"geofencing_sub:{sub_id}")
    if not isinstance(sink, bytes):
        return
    if (
        notification.monitoringEventReports is None
        or notification.monitoringEventReports[0].externalId is None
    ):
        return
    event = CloudEvent(
        id="ola",
        type=NotificationEventType.org_camaraproject_geofencing_subscriptions_v0_area_entered,
        time=DateTime(datetime.now()),
        data=AreaLeft(
            device=Device(
                networkAccessIdentifier=NetworkAccessIdentifier(
                    notification.monitoringEventReports[0].externalId.root
                )
            ),
            area=Area(areaType=AreaType.CIRCLE),
            subscriptionId=SubscriptionId("ola"),
        ).model_dump(),
        source=Source("test"),
    )

    requests.post(sink, data=event.model_dump_json())


@router.get("/subscriptions")
def get_subscritpions() -> None:
    content = {
        "status": HTTPStatus.NOT_IMPLEMENTED,
        "code": "NOT_IMPLEMENTED",
        "message": "Endpoint not implemented",
    }
    raise HTTPException(status_code=HTTPStatus.NOT_IMPLEMENTED, detail=content)


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
