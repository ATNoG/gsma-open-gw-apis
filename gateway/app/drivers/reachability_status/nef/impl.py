import enum
import asyncio
import logging
from datetime import datetime
from typing import Optional

from pydantic import AnyHttpUrl, AnyUrl
from fastapi.encoders import jsonable_encoder

from app.settings import NEFSettings
from app.schemas.device import Device
from app.interfaces.reachability_status import ReachabilityStatusInterface
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringEventReport,
    MonitoringEventSubscription,
    MonitoringType,
    ReachabilityType,
)
from app.schemas.reachability_status import (
    CloudEventData,
    ConnectivityType,
    CreateSubscriptionDetail,
    NotificationEventType,
    ReachabilityStatusResponse,
    Subscription,
    SubscriptionEnds,
    SubscriptionEventType,
    SubscriptionRequest,
    SubscriptionTypeAdapter,
)
from app.schemas.subscriptions import (
    TerminationReason,
)
from app.utils.nef_driver_base import NefDriverBase
from app.utils.subscription_driver_redis import SubscriptionDriverRedis

_prefix_nef_url = "reachability_status_nef_url"


class _ConnectivityStatus(enum.Enum):
    Connected = enum.auto()
    NoConnectivity = enum.auto()
    Unknown = enum.auto()


class NefReachabilityStatusInterface(
    ReachabilityStatusInterface,
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
            self, source, "reachability_status", SubscriptionTypeAdapter
        )

        self.notification_url = nef_settings.get_notification_url()

    async def _check_connectivity(
        self, device: Device, type: ReachabilityType
    ) -> _ConnectivityStatus:
        sub = MonitoringEventSubscription(
            monitoringType=MonitoringType.UE_REACHABILITY,
            notificationDestination=AnyHttpUrl("https://0.0.0.0"),
            maximumNumberOfReports=1,
            addnMonTypes=[MonitoringType.LOSS_OF_CONNECTIVITY],
            reachabilityType=type,
        )

        sub = self.install_device_identifiers(sub, device)

        res = await self.httpx_client.post(
            f"3gpp-monitoring-event/v1/{self.af_id}/subscriptions",
            json=jsonable_encoder(sub, exclude_unset=True),
        )

        if not res.is_success:
            logging.error("Failed to create NEF subscription")
            raise RuntimeError()

        # No report was available so the device doesn't have data but also
        # isn't disconnected.
        if res.status_code == 201:
            sub = MonitoringEventSubscription.model_validate(res.json())
            assert sub.self is not None
            asyncio.create_task(self.delete_nef_subscription(sub.self))
            return _ConnectivityStatus.Unknown

        report = MonitoringEventReport.model_validate(res.json())

        if report.monitoringType == "LOSS_OF_CONNECTIVITY":
            return _ConnectivityStatus.NoConnectivity
        elif report.monitoringType == "UE_REACHABILITY":
            return _ConnectivityStatus.Connected

        return _ConnectivityStatus.Unknown

    async def get_reachability_status(
        self, device: Device
    ) -> ReachabilityStatusResponse:
        res = ReachabilityStatusResponse(lastStatusTime=datetime.now(), reachable=False)

        data_connectivity = await self._check_connectivity(
            device, ReachabilityType.DATA
        )

        if data_connectivity == _ConnectivityStatus.NoConnectivity:
            res.reachable = False
            return res
        elif data_connectivity == _ConnectivityStatus.Connected:
            res.reachable = True
            res.connectivity = [ConnectivityType.DATA]

        sms_connectivity = await self._check_connectivity(device, ReachabilityType.SMS)

        if sms_connectivity == _ConnectivityStatus.NoConnectivity:
            res.reachable = False
            res.connectivity = None
            return res
        elif data_connectivity == _ConnectivityStatus.Connected:
            res.reachable = True
            if res.connectivity is None:
                res.connectivity = []
            res.connectivity.append(ConnectivityType.SMS)

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

        # Create monitoring event subscription
        monType: MonitoringType
        reachabilityType: Optional[ReachabilityType] = None

        match req.types[0]:
            case SubscriptionEventType.v0_reachability_data:
                monType = MonitoringType.UE_REACHABILITY
                reachabilityType = ReachabilityType.DATA
            case SubscriptionEventType.v0_reachability_sms:
                monType = MonitoringType.UE_REACHABILITY
                reachabilityType = ReachabilityType.SMS
            case SubscriptionEventType.v0_reachability_disconnected:
                monType = MonitoringType.LOSS_OF_CONNECTIVITY

        try:
            body = MonitoringEventSubscription(
                notificationDestination=AnyUrl(
                    f"{self.notification_url}/callbacks/v1/reachability-status/{sub.id}"
                ),
                monitoringType=monType,
                reachabilityType=reachabilityType,
                monitorExpireTime=req.config.subscriptionExpireTime or datetime.max,
                immediateRep=req.config.initialEvent,
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

        # Delete all the redis data besides the subscription
        await self.redis.delete(nef_url_key)

        await self.notify_sink(
            subscription,
            NotificationEventType.v0_subscription_ends,
            SubscriptionEnds(
                terminationReason=termination_reason,
                device=subscription.config.subscriptionDetail.device,
                subscriptionId=sub_id,
            ),
        )
