import uuid
import enum
import asyncio
import logging
from datetime import datetime, timezone
from typing import Never, Optional

import httpx
from pydantic import AnyHttpUrl, AnyUrl
from fastapi.encoders import jsonable_encoder

from app.settings import NEFSettings
from app.exceptions import ResourceNotFound
from app.redis import get_redis
from app.schemas.device import Device
from app.drivers.nef_auth import NEFAuth
from app.interfaces.reachability_status import ReachabilityStatusInterface
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringEventReport,
    MonitoringEventSubscription,
    MonitoringType,
    ReachabilityType,
)
from app.schemas.reachability_status import (
    CloudEvent,
    ConnectivityType,
    NotificationEventType,
    ReachabilityDataSmsDisconnected,
    ReachabilityStatusResponse,
    Subscription,
    SubscriptionEnds,
    SubscriptionEventType,
    SubscriptionRequest,
    SubscriptionTypeAdapter,
)
from app.schemas.subscriptions import (
    HTTPSubscriptionResponse,
    Protocol,
    SubscriptionStatus,
    TerminationReason,
)

_prefix_subscription = "reachability_status"
_prefix_counter = "reachability_status_counter"
_prefix_nef_url = "reachability_status_nef_url"

_termination_reason_to_status = {
    TerminationReason.SUBSCRIPTION_DELETED: SubscriptionStatus.DELETED,
    TerminationReason.SUBSCRIPTION_EXPIRED: SubscriptionStatus.EXPIRED,
    TerminationReason.MAX_EVENTS_REACHED: SubscriptionStatus.EXPIRED,
}


class _ConnectivityStatus(enum.Enum):
    Connected = enum.auto()
    NoConnectivity = enum.auto()
    Unknown = enum.auto()


class NefReachabilityStatusInterface(ReachabilityStatusInterface):
    def __init__(self, nef_settings: NEFSettings, source: str) -> None:
        super().__init__()

        nef_auth = NEFAuth(
            nef_settings.url, nef_settings.username, nef_settings.password
        )
        self.httpx_client = httpx.AsyncClient(
            base_url=nef_settings.get_base_url(), auth=nef_auth
        )
        self.httpx_client_callback = httpx.AsyncClient()

        self.af_id = nef_settings.gateway_af_id
        self.source = source
        self.notification_url = nef_settings.get_notification_url()

        self.redis = get_redis()

    async def delete_nef_subscription(self, sub_url: AnyUrl | str) -> None:
        res = await self.httpx_client.delete(str(sub_url))

        if res.status_code == 404:
            logging.warning("Subscription not found")
            return

        if not res.is_success:
            logging.error(
                "Failed to delete NEF subscription (code: {%d}): %s",
                res.status_code,
                res.text,
            )

    def _install_device_identifiers(
        self, sub: MonitoringEventSubscription, device: Device
    ) -> MonitoringEventSubscription:
        if device.phoneNumber is not None:
            sub.msisdn = device.phoneNumber.lstrip("+")
        elif device.ipv4Address is not None:
            sub.ipv4Addr = device.ipv4Address.publicAddress
        elif device.ipv6Address is not None:
            sub.ipv6Addr = device.ipv6Address
        elif device.networkAccessIdentifier is not None:
            sub.externalId = device.networkAccessIdentifier

        return sub

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

        sub = self._install_device_identifiers(sub, device)

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

    async def clear_loop(self) -> Never:
        while True:
            try:
                logging.debug("Clearing expired subscriptions")
                await self._clear_expired_subscriptions()
                await asyncio.sleep(5)
            except Exception as e:
                logging.error(e)

    async def _clear_expired_subscriptions(self) -> None:
        keys = await self.redis.keys(f"{_prefix_subscription}:*")

        for key in keys:
            sub_key = f"{_prefix_subscription}:{key.split(':')[1]}"
            sub = await self.redis.get(sub_key)
            if sub is None:
                continue

            sub = SubscriptionTypeAdapter.validate_json(sub)
            if (
                sub.status != SubscriptionStatus.ACTIVE
                or sub.config.subscriptionExpireTime is None
                or datetime.now(sub.config.subscriptionExpireTime.tzinfo)
                < sub.config.subscriptionExpireTime
            ):
                continue

            await self.delete_subscription(
                sub.id, termination_reason=TerminationReason.SUBSCRIPTION_EXPIRED
            )

    async def create_subscription(
        self, req: SubscriptionRequest, device: Device
    ) -> Subscription:
        # Store subscription
        req.config.subscriptionDetail.device = device
        sub_id = str(uuid.uuid4())
        sub: Subscription = HTTPSubscriptionResponse(
            protocol=Protocol.HTTP,
            sink=req.sink,
            types=req.types,
            config=req.config,
            startsAt=datetime.now(
                timezone.utc
                if req.config.subscriptionExpireTime is None
                else req.config.subscriptionExpireTime.tzinfo
            ),
            id=sub_id,
            expiresAt=req.config.subscriptionExpireTime,
            status=SubscriptionStatus.ACTIVE,
        )

        sub_key = f"{_prefix_subscription}:{sub_id}"
        await self.redis.set(sub_key, sub.model_dump_json(exclude_unset=True))

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

        body = MonitoringEventSubscription(
            notificationDestination=AnyUrl(
                f"{self.notification_url}/callbacks/v1/reachability-status/{sub_id}"
            ),
            monitoringType=monType,
            reachabilityType=reachabilityType,
            monitorExpireTime=req.config.subscriptionExpireTime or datetime.max,
            immediateRep=req.config.initialEvent,
        )

        body = self._install_device_identifiers(body, device)

        res = await self.httpx_client.post(
            f"3gpp-monitoring-event/v1/{self.af_id}/subscriptions",
            json=jsonable_encoder(body, exclude_unset=True, exclude_none=True),
        )

        # Check success of monitoring event subscription
        if not res.is_success:
            await self.redis.delete(sub_key)
            raise RuntimeError()

        subscription_result = MonitoringEventSubscription.model_validate_json(
            res.content
        )

        if subscription_result.self is None:
            logging.error("No 'self' in monitoring subscription response")
            await self.redis.delete(sub_key)
            raise RuntimeError()

        self_key = f"{_prefix_nef_url}:{sub_id}"
        await self.redis.set(self_key, subscription_result.self.unicode_string())

        return sub

    async def delete_subscription(
        self,
        sub_id: str,
        *,
        nef_subscription_url: Optional[str] = None,
        termination_reason: TerminationReason = TerminationReason.SUBSCRIPTION_DELETED,
    ) -> None:
        subscription_key = f"{_prefix_subscription}:{sub_id}"
        subscription = await self.redis.get(subscription_key)
        if subscription is None:
            raise ResourceNotFound()

        nef_url_key = f"{_prefix_nef_url}:{sub_id}"

        if nef_subscription_url is None:
            nef_subscription_url = await self.redis.get(nef_url_key)

        if nef_subscription_url is not None:
            # Schedule the deletion of the NEF subscription
            asyncio.create_task(self.delete_nef_subscription(nef_subscription_url))

        # Delete all the redis data besides the subscription
        counter_key = f"{_prefix_counter}:{sub_id}"
        await self.redis.delete(counter_key, nef_url_key)

        subscription = SubscriptionTypeAdapter.validate_json(subscription)
        subscription.status = _termination_reason_to_status[termination_reason]
        await self.redis.set(
            subscription_key, subscription.model_dump_json(exclude_unset=True)
        )

        res = CloudEvent(
            id=str(uuid.uuid4()),
            source=self.source,
            type=NotificationEventType.v0_subscription_ends,
            time=datetime.now(
                timezone.utc
                if subscription.config.subscriptionExpireTime is None
                else subscription.config.subscriptionExpireTime.tzinfo
            ),
            data=SubscriptionEnds(
                terminationReason=termination_reason,
                device=subscription.config.subscriptionDetail.device,
                subscriptionId=sub_id,
            ),
        )

        asyncio.create_task(
            self.httpx_client_callback.post(
                subscription.sink,
                json=jsonable_encoder(res, exclude_unset=True),
            )
        )

    async def get_subscription(self, sub_id: str) -> Subscription:
        key = f"{_prefix_subscription}:{sub_id}"

        result = await self.redis.get(key)

        if result is None:
            raise ResourceNotFound()

        return SubscriptionTypeAdapter.validate_json(result)

    async def get_subscriptions(self) -> list[Subscription]:
        keys = await self.redis.keys(f"{_prefix_subscription}:*")
        subscriptions: list[Subscription] = []

        for key in keys:
            result = await self.redis.get(key)
            if result is None:
                continue
            subscriptions.append(SubscriptionTypeAdapter.validate_json(result))

        return subscriptions

    async def notify_sink(
        self,
        subscription: Subscription,
        nef_subscription_url: str,
        type: NotificationEventType,
    ) -> None:
        if subscription.config.subscriptionMaxEvents is not None:
            counter_key = f"{_prefix_counter}:{subscription.id}"
            counter = await self.redis.incr(counter_key)

            if counter >= subscription.config.subscriptionMaxEvents:
                await self.delete_subscription(
                    subscription.id,
                    nef_subscription_url=nef_subscription_url,
                    termination_reason=TerminationReason.MAX_EVENTS_REACHED,
                )

        res = CloudEvent(
            id=str(uuid.uuid4()),
            source=self.source,
            type=type,
            time=datetime.now(
                timezone.utc
                if subscription.config.subscriptionExpireTime is None
                else subscription.config.subscriptionExpireTime.tzinfo
            ),
            data=ReachabilityDataSmsDisconnected(
                device=subscription.config.subscriptionDetail.device,
                subscriptionId=subscription.id,
            ),
        )

        asyncio.create_task(
            self.httpx_client_callback.post(
                subscription.sink, json=jsonable_encoder(res, exclude_unset=True)
            )
        )
