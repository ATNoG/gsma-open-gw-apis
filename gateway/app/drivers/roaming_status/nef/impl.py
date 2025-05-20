from typing import Optional
import asyncio
import logging
from datetime import datetime

from pydantic import AnyHttpUrl, AnyUrl
from fastapi.encoders import jsonable_encoder

from app.interfaces.roaming_status import (
    RoamingStatusInterface,
    RoamingStatusSubscriptionInterface,
)
from app.schemas.roaming_status import (
    CloudEventData,
    CreateSubscriptionDetail,
    NotificationEventType,
    RoamingStatusResponse,
    SubscriptionEnds,
    SubscriptionEventType,
    SubscriptionTypeAdapter,
)
from app.schemas.subscriptions import (
    TerminationReason,
)
from app.settings import NEFSettings
from app.schemas.device import Device
from app.utils.nef_driver_base import NefDriverBase
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringEventReport,
    MonitoringEventSubscription,
    MonitoringType,
)
from app.schemas.roaming_status import Subscription, SubscriptionRequest
from app.utils.subscription_driver_redis import SubscriptionDriverRedis

_prefix_nef_url = "roaming_status_nef_url"
_prefix_roaming_state = "roaming_status_state"


class UnknownRoamingState:
    pass


type RoamingState = UnknownRoamingState | None | int


class NefRoamingStatusInterface(
    RoamingStatusInterface,
    RoamingStatusSubscriptionInterface,
    NefDriverBase,
    SubscriptionDriverRedis[
        SubscriptionEventType,
        CreateSubscriptionDetail,
        NotificationEventType,
        CloudEventData,
    ],
):
    def __init__(self, nef_settings: NEFSettings, source: str) -> None:
        NefDriverBase.__init__(self, nef_settings)
        SubscriptionDriverRedis.__init__(
            self, source, "roaming_status", SubscriptionTypeAdapter
        )

        self.notification_url = nef_settings.get_notification_url()

    async def get_roaming_status(self, device: Device) -> RoamingStatusResponse:
        sub = MonitoringEventSubscription(
            monitoringType=MonitoringType.ROAMING_STATUS,
            notificationDestination=AnyHttpUrl("https://0.0.0.0"),
            maximumNumberOfReports=1,
            plmnIndication=True,
        )

        sub = self.install_device_identifiers(sub, device)

        nef_res = await self.httpx_client.post(
            f"3gpp-monitoring-event/v1/{self.af_id}/subscriptions",
            json=jsonable_encoder(sub, exclude_unset=True),
        )

        if not nef_res.is_success:
            logging.error("Failed to create NEF subscription")
            raise RuntimeError()

        if nef_res.status_code == 201:
            sub = MonitoringEventSubscription.model_validate(nef_res.json())
            assert sub.self is not None
            asyncio.create_task(self.delete_nef_subscription(sub.self))
            raise RuntimeError("Expected report received subscription")

        report = MonitoringEventReport.model_validate(nef_res.json())
        assert report.roamingStatus is not None

        res = RoamingStatusResponse(
            lastStatusTime=datetime.now(),
            roaming=report.roamingStatus,
        )

        if report.roamingStatus and report.plmnId is not None:
            res.countryCode = report.plmnId.mcc

        return res

    async def get_subscription(self, sub_id: str) -> Subscription:
        return await SubscriptionDriverRedis.get_subscription(self, sub_id)

    async def get_subscriptions(self) -> list[Subscription]:
        return await SubscriptionDriverRedis.get_subscriptions(self)

    async def create_subscription(
        self, req: SubscriptionRequest, device: Device
    ) -> Subscription:
        req.config.subscriptionDetail.device = device
        sub = await self.create_gateway_subscription(req)

        try:
            # Create monitoring event subscription
            body = MonitoringEventSubscription(
                notificationDestination=AnyUrl(
                    f"{self.notification_url}/callbacks/v1/roaming-status/{sub.id}"
                ),
                monitoringType=MonitoringType.ROAMING_STATUS,
                monitorExpireTime=req.config.subscriptionExpireTime or datetime.max,
                immediateRep=req.config.initialEvent,
                plmnIndication=True,
            )

            body = self.install_device_identifiers(body, device)

            res = await self.httpx_client.post(
                f"3gpp-monitoring-event/v1/{self.af_id}/subscriptions",
                json=jsonable_encoder(body, exclude_unset=True, exclude_none=True),
            )

            # Check success of monitoring event subscription
            if not res.is_success:
                raise RuntimeError()

            subscription_result = MonitoringEventSubscription.model_validate_json(
                res.content
            )

            if subscription_result.self is None:
                logging.error("No 'self' in monitoring subscription response")
                raise RuntimeError()

            self_key = f"{_prefix_nef_url}:{sub.id}"
            await self.redis.set(self_key, subscription_result.self.unicode_string())

            return sub
        except BaseException as e:
            await self.permanently_delete_subscription(sub)
            raise e

    def _state_key(self, id: str) -> str:
        return f"{_prefix_roaming_state}:{id}"

    async def delete_subscription(
        self,
        sub_id: str,
        *,
        nef_subscription_url: Optional[str] = None,
        termination_reason: TerminationReason = TerminationReason.SUBSCRIPTION_DELETED,
    ) -> None:
        subscription = await self.delete_gateway_subscription(
            sub_id, termination_reason
        )

        if subscription is None:
            return

        nef_url_key = f"{_prefix_nef_url}:{sub_id}"

        if nef_subscription_url is None:
            nef_subscription_url = await self.redis.get(nef_url_key)

        if nef_subscription_url is not None:
            # Schedule the deletion of the NEF subscription
            asyncio.create_task(self.delete_nef_subscription(nef_subscription_url))

        await self.redis.delete(nef_url_key, self._state_key(sub_id))

        await self.notify_sink(
            subscription,
            NotificationEventType.v0_subscription_ends,
            SubscriptionEnds(
                terminationReason=termination_reason,
                device=subscription.config.subscriptionDetail.device,
                subscriptionId=sub_id,
            ),
        )

    async def get_last_roaming_state(self, id: str) -> RoamingState:
        res = await self.redis.get(self._state_key(id))

        if res is None:
            return UnknownRoamingState()

        mcc = int(res)
        if mcc <= 0:
            return None
        else:
            return mcc

    async def save_roaming_state(self, id: str, plmnid: Optional[int]) -> None:
        key = self._state_key(id)
        if plmnid is not None:
            await self.redis.set(key, plmnid)
        else:
            await self.redis.set(key, -1)
