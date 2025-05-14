import logging
from http import HTTPStatus

from fastapi import APIRouter

from app.drivers.geofencing.nef import nef_geofencing_subscription_interface
from app.interfaces.geofencing_subscriptions import GeofencingSubscriptionNotFound
from app.schemas.geofencing import Subscription
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringNotification,
    SupportedGADShapes,
)

router = APIRouter()

LOG = logging.getLogger(__name__)


@router.post("/geofencing/{sub_id}", status_code=HTTPStatus.NO_CONTENT)
async def webhook(sub_id: str, notification: MonitoringNotification) -> None:
    LOG.debug(notification)

    if (
        notification.monitoringEventReports is None
        or notification.monitoringEventReports[0].locationInfo is None
        or notification.monitoringEventReports[0].locationInfo.geographicArea is None
    ):
        LOG.warning("No location details in received notification")
        return

    geographicArea = notification.monitoringEventReports[0].locationInfo.geographicArea
    if geographicArea.shape != SupportedGADShapes.POINT:
        LOG.warning("Received shape is not a POINT")
        return

    point = geographicArea.point
    subscription: Subscription
    try:
        subscription = await nef_geofencing_subscription_interface.get_subscription(
            sub_id
        )
    except GeofencingSubscriptionNotFound:
        LOG.warning("Received notification for non exisiting subscription")
        return

    await nef_geofencing_subscription_interface._notify_location(
        subscription, point, endpoint=notification.subscription.unicode_string()
    )
