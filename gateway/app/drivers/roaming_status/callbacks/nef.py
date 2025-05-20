import asyncio
import logging
from http import HTTPStatus
from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.drivers.roaming_status.nef.impl import UnknownRoamingState
from app.exceptions import ResourceNotFound
from app.drivers.roaming_status.nef import nef_roaming_status_interface
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringNotification,
    MonitoringType,
)
from app.schemas.roaming_status import (
    BasicDeviceEventData,
    CloudEventData,
    NotificationEventType,
    RoamingChangeCountry,
    RoamingStatus,
    SubscriptionEventType,
)
from app.schemas.subscriptions import SubscriptionStatus
from app.utils.mcc_to_country_code import get_country_names


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(nef_roaming_status_interface.clear_loop())

    yield

    task.cancel()


router = APIRouter(lifespan=lifespan)


@router.post("/roaming-status/{sub_id}", status_code=HTTPStatus.NO_CONTENT)
async def webhook(sub_id: str, notification: MonitoringNotification) -> None:
    logging.debug(notification)

    if notification.monitoringEventReports is None:
        logging.debug("Received notification with no event reports")
        return

    try:
        subscription = await nef_roaming_status_interface.get_subscription(sub_id)
    except ResourceNotFound:
        logging.warning("Received notification for non exisiting subscription")
        asyncio.create_task(
            nef_roaming_status_interface.delete_nef_subscription(
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
                nef_roaming_status_interface.delete_nef_subscription(
                    notification.subscription
                )
            )
        return

    last_state = await nef_roaming_status_interface.get_last_roaming_state(
        subscription.id
    )

    for report in notification.monitoringEventReports:
        if (
            report.monitoringType != MonitoringType.ROAMING_STATUS
            or report.roamingStatus is None
        ):
            continue

        await nef_roaming_status_interface.save_roaming_state(
            subscription.id,
            (report.plmnId.mcc if report.plmnId is not None else 1)
            if report.roamingStatus
            else None,
        )

        for sub_type in subscription.types:
            notif_type: NotificationEventType
            data: CloudEventData

            if SubscriptionEventType.v0_roaming_status == sub_type:
                if (
                    not isinstance(last_state, UnknownRoamingState)
                    and last_state is not None == report.roamingStatus
                ):
                    continue

                notif_type = NotificationEventType.v0_roaming_status
                data = RoamingStatus(
                    device=subscription.config.subscriptionDetail.device,
                    roaming=report.roamingStatus,
                    subscriptionId=subscription.id,
                )
            elif SubscriptionEventType.v0_roaming_on == sub_type:
                if not (
                    # If this is an initial event and the device is roaming we want to send a notification
                    (
                        isinstance(last_state, UnknownRoamingState)
                        and subscription.config.initialEvent
                        and report.roamingStatus
                    )
                    # Otherwise we only send it when the previous state was not roaming and now it's roaming
                    or (last_state is None and report.roamingStatus)
                ):
                    continue

                notif_type = NotificationEventType.v0_roaming_on
                data = BasicDeviceEventData(
                    device=subscription.config.subscriptionDetail.device,
                    subscriptionId=subscription.id,
                )
            elif SubscriptionEventType.v0_roaming_off == sub_type:
                if not (
                    # If this is an initial event and the device is not roaming we want to send a notification
                    (
                        isinstance(last_state, UnknownRoamingState)
                        and subscription.config.initialEvent
                        and not report.roamingStatus
                    )
                    # Otherwise we only send it when the previous state was roaming and it isn't roaming
                    or (type(last_state) is int and not report.roamingStatus)
                ):
                    continue

                notif_type = NotificationEventType.v0_roaming_off
                data = BasicDeviceEventData(
                    device=subscription.config.subscriptionDetail.device,
                    subscriptionId=subscription.id,
                )
            elif SubscriptionEventType.v0_roaming_change_country == sub_type:
                if (
                    isinstance(last_state, UnknownRoamingState)
                    or last_state is None
                    or not report.roamingStatus
                    or report.plmnId is None
                ):
                    continue

                before_countries = get_country_names(last_state)
                after_countries = get_country_names(report.plmnId.mcc)

                if before_countries != after_countries:
                    notif_type = NotificationEventType.v0_roaming_change_country
                    data = RoamingChangeCountry(
                        device=subscription.config.subscriptionDetail.device,
                        subscriptionId=subscription.id,
                        countryCode=report.plmnId.mcc,
                        countryName=after_countries,
                    )
                else:
                    continue
            else:
                logging.error("Unhandled subscription type: %s", sub_type)
                continue

            await nef_roaming_status_interface.send_report(
                subscription,
                notif_type,
                data,
                nef_subscription_url=str(notification.subscription),
            )
