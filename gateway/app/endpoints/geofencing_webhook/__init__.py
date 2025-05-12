import logging

from fastapi import APIRouter
from pydantic import AnyUrl

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.interfaces.geofencing_subscriptions import GeofencingSubscriptionNotFound
from app.schemas.geofencing import MonitoringNotification, Subscription

router = APIRouter()

LOG = logging.getLogger(__name__)


def _get_nef_sub_from_subscription_url(url: AnyUrl | None) -> str:
    if url is None or url.path is None:
        raise Exception("Invalid url")

    return url.path.rsplit("/")[-1]


@router.post("/geofencing/webhook")
async def webhook(
    notification: MonitoringNotification,
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> None:
    LOG.debug(notification)
    nef_sub = _get_nef_sub_from_subscription_url(notification.subscription)
    await geofencing_subscription_interface.clear_expired_subscriptions()

    if (
        notification.monitoringEventReports is None
        or notification.monitoringEventReports[0].locationInfo is None
        or notification.monitoringEventReports[0].locationInfo.geographicArea is None
    ):
        LOG.debug("No location details in received notification")
        return

    point = notification.monitoringEventReports[0].locationInfo.geographicArea.point
    subscription: Subscription
    try:
        subscription = await geofencing_subscription_interface.get_subscription(nef_sub)
    except GeofencingSubscriptionNotFound:
        await geofencing_subscription_interface.queue_notification(nef_sub, point)
        return
    await geofencing_subscription_interface.notify_location(subscription, point)
