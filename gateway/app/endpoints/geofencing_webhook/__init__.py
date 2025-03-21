import logging
from fastapi import APIRouter
from pydantic import AnyUrl

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.schemas.geofencing import MonitoringNotification


router = APIRouter()

LOG = logging.getLogger(__name__)


def _get_subscription_id_from_subscription_url(url: AnyUrl | None) -> str:
    if url is None or url.path is None:
        raise Exception("Invalid url")

    return url.path.rsplit("/")[-1]


@router.post("/geofencing/webhook")
async def webhook(
    notification: MonitoringNotification,
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> None:
    print(notification)
    id = _get_subscription_id_from_subscription_url(notification.subscription)

    subscription = await geofencing_subscription_interface.get_subscription(id)

    if (
        notification.monitoringEventReports is None
        or notification.monitoringEventReports[0].locationInfo is None
        or notification.monitoringEventReports[0].locationInfo.geographicArea is None
    ):
        LOG.debug("No location details in received notification")
        return

    point = notification.monitoringEventReports[0].locationInfo.geographicArea.point
    await geofencing_subscription_interface.notify_location(subscription, point)
