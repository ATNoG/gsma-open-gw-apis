import asyncio
import logging
from http import HTTPStatus
from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.exceptions import ResourceNotFound
from app.drivers.geofencing.nef import nef_geofencing_subscription_interface
from app.schemas.geofencing import Subscription
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringNotification,
    SupportedGADShapes,
)

LOG = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(nef_geofencing_subscription_interface.clear_loop())

    yield

    task.cancel()


router = APIRouter(lifespan=lifespan)


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
    except ResourceNotFound:
        LOG.warning("Received notification for non exisiting subscription")
        return

    await nef_geofencing_subscription_interface.notify_location(
        subscription,
        point,
        nef_subscription_url=notification.subscription.unicode_string(),
    )
