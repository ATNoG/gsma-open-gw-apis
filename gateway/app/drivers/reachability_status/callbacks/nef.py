import asyncio
import logging
from http import HTTPStatus
from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.exceptions import ResourceNotFound
from app.drivers.reachability_status.nef import nef_reachability_status_interface
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringNotification,
    MonitoringType,
    ReachabilityType,
)
from app.schemas.reachability_status import NotificationEventType
from app.schemas.subscriptions import SubscriptionStatus


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(nef_reachability_status_interface.clear_loop())

    yield

    task.cancel()


router = APIRouter(lifespan=lifespan)


@router.post("/reachability-status/{sub_id}", status_code=HTTPStatus.NO_CONTENT)
async def webhook(sub_id: str, notification: MonitoringNotification) -> None:
    logging.debug(notification)

    if notification.monitoringEventReports is None:
        logging.debug("Received notification with no event reports")
        return

    try:
        subscription = await nef_reachability_status_interface.get_subscription(sub_id)
    except ResourceNotFound:
        logging.warning("Received notification for non exisiting subscription")
        asyncio.create_task(
            nef_reachability_status_interface.delete_nef_subscription(
                notification.subscription
            )
        )
        return

    if subscription.status != SubscriptionStatus.ACTIVE:
        logging.warning("Received notification for inactive subscription")
        if subscription.status in (
            SubscriptionStatus.EXPIRED,
            SubscriptionStatus.DELETED,
        ):
            asyncio.create_task(
                nef_reachability_status_interface.delete_nef_subscription(
                    notification.subscription
                )
            )
        return

    for report in notification.monitoringEventReports:
        type: NotificationEventType
        if report.monitoringType == MonitoringType.UE_REACHABILITY:
            if report.reachabilityType == ReachabilityType.DATA:
                type = NotificationEventType.v0_reachability_data
            elif report.reachabilityType == ReachabilityType.SMS:
                type = NotificationEventType.v0_reachability_sms
            else:
                logging.warning(
                    "Received unexpected reachability type: %s", report.reachabilityType
                )
                continue
        elif report.monitoringType == MonitoringType.LOSS_OF_CONNECTIVITY:
            type = NotificationEventType.v0_reachability_disconnected
        else:
            logging.warning(
                "Received unexpected monitoring type: %s", report.monitoringType
            )
            continue

        await nef_reachability_status_interface.notify_sink(
            subscription, notification.subscription.unicode_string(), type
        )
