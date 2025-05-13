import asyncio
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from http import HTTPStatus
from typing import Never, Optional

import geopy  # type: ignore[import-untyped]
import geopy.distance  # type: ignore[import-untyped]
import httpx
from pydantic import AnyHttpUrl, AnyUrl

from app.drivers.nef_auth import NEFAuth
from app.exceptions import ApiException
from app.interfaces.geofencing_subscriptions import (
    GeofencingSubscriptionInterface,
    GeofencingSubscriptionNotFound,
)
from app.redis import get_redis
from app.schemas.device import Device
from app.schemas.geofencing import (
    AreaEntered,
    AreaLeft,
    CloudEvent,
    NotificationEventType,
    Protocol,
    Status,
    Subscription,
    SubscriptionEnds,
    SubscriptionEventType,
    SubscriptionRequest,
    TerminationReason,
)
from app.schemas.nef_schemas.monitoringevent import (
    GeographicalCoordinates,
    MonitoringEventSubscription,
    MonitoringType,
)
from app.settings import settings

LOG = logging.getLogger(__name__)

_prefix_subscription = "geofencing"
_prefix_last_state = "geofencing_state"
_prefix_counter = "geofencing_counter"
_prefix_nef_url = "geofencing_nef_url"


class State(str, Enum):
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


def _handle_post_error(res: httpx.Response) -> None:
    raise ApiException(
        message="Error comunicating with the core",
    )


class NefGeofencingSubscriptionInterface(GeofencingSubscriptionInterface):
    def __init__(self, nef_url: AnyHttpUrl, nef_auth: NEFAuth) -> None:
        super().__init__()
        self.httpx_client = httpx.AsyncClient(base_url=str(nef_url), auth=nef_auth)
        self.redis = get_redis()

    async def _clear_loop(self) -> Never:
        while True:
            try:
                LOG.info("Clearing expired subscriptions")
                await self._clear_expired_subscriptions()
                await asyncio.sleep(5)
            except Exception as e:
                LOG.error(e)

    async def _clear_expired_subscriptions(self) -> None:
        keys = await self.redis.keys(f"{_prefix_nef_url}:*")

        for key in keys:
            sub_key = f"{_prefix_subscription}:{key.split(':')[1]}"
            sub = await self.redis.get(sub_key)
            if sub is None:
                continue

            sub = Subscription.model_validate_json(sub)
            if (
                sub.config.subscriptionExpireTime is None
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
        # Validation
        if req.protocol != Protocol.HTTP:
            raise ApiException(
                status=HTTPStatus.BAD_REQUEST,
                code="INVALID_PROTOCOL",
                message="Only HTTP is supported.",
            )

        if (
            device.phoneNumber is None
            and device.ipv4Address is None
            and device.ipv6Address is None
        ):
            raise ApiException(
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
                code="UNSUPPORTED_IDENTIFIER",
                message="The identifier provided is not supported.",
            )

        # Store subscription
        req.config.subscriptionDetail.device = device
        sub_id = str(uuid.uuid4())
        sub = Subscription(
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
            status=Status.ACTIVE,
        )

        sub_key = f"{_prefix_subscription}:{sub_id}"
        await self.redis.set(sub_key, sub.model_dump_json())

        # Create monitoring event subscription
        number = None
        if device.phoneNumber is not None:
            number = device.phoneNumber[1:]

        ipv4 = None
        if device.ipv4Address is not None:
            ipv4 = device.ipv4Address.publicAddress

        body = MonitoringEventSubscription(
            msisdn=number,
            ipv6Addr=device.ipv6Address,
            ipv4Addr=ipv4,
            notificationDestination=AnyUrl(
                f"{settings.nef_gateway_url}callbacks/v1/geofencing/{sub_id}"
            ),
            monitoringType=MonitoringType.LOCATION_REPORTING,
            monitorExpireTime=req.config.subscriptionExpireTime or datetime.max,
            immediateRep=req.config.initialEvent,
        )

        res = await self.httpx_client.post(
            f"{settings.geofencing.monitoring_base_path}/subscriptions",
            content=body.model_dump_json(),
        )

        # Check success of monitoring event subscription
        if not res.is_success:
            await self.redis.delete(sub_key)
            _handle_post_error(res)

        subscription_result = MonitoringEventSubscription.model_validate_json(
            res.content
        )

        if subscription_result.self is None:
            LOG.error("No 'self' in monitoring subscription response")
            await self.redis.delete(sub_key)
            raise ApiException(
                message="Error comunicating with the core",
            )

        self_key = f"{_prefix_nef_url}:{sub_id}"
        await self.redis.set(self_key, subscription_result.self.unicode_string())

        return sub

    def _get_subscription_id_from_subscription_url(self, url: AnyUrl) -> str:
        if url.path is None:
            raise Exception("Invalid url")

        return url.path.rsplit("/")[-1]

    async def delete_subscription(
        self,
        id: str,
        *,
        endpoint: Optional[str] = None,
        termination_reason: TerminationReason = TerminationReason.SUBSCRIPTION_DELETED,
    ) -> None:
        subscription_key = f"{_prefix_subscription}:{id}"
        last_state_key = f"{_prefix_last_state}:{id}"
        counter_key = f"{_prefix_counter}:{id}"
        url_key = f"{_prefix_nef_url}:{id}"

        subscription = await self.redis.get(subscription_key)
        if subscription is None:
            raise GeofencingSubscriptionNotFound()

        url: str
        if endpoint is None:
            url = await self.redis.get(url_key)
        else:
            url = endpoint

        await self.httpx_client.delete(url)

        await self.redis.delete(subscription_key)
        await self.redis.delete(last_state_key)
        await self.redis.delete(counter_key)
        await self.redis.delete(url_key)

        subscription = Subscription.model_validate_json(subscription)

        res = CloudEvent(
            id=subscription.id,
            source=settings.geofencing.geofencing_url.unicode_string(),
            type=NotificationEventType.v0_subscription_ends,
            time=datetime.now(
                timezone.utc
                if subscription.config.subscriptionExpireTime is None
                else subscription.config.subscriptionExpireTime.tzinfo
            ),
            data=SubscriptionEnds(
                terminationReason=termination_reason,
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=subscription.id,
            ),
        )

        await self.httpx_client.post(
            subscription.sink,
            content=res.model_dump_json(),
            headers={"Content-Type": "application/json"},
        )

    async def get_subscription(self, id: str) -> Subscription:
        key = f"{_prefix_subscription}:{id}"

        result = await self.redis.get(key)

        if result is None:
            raise GeofencingSubscriptionNotFound()

        return Subscription.model_validate_json(result)

    async def get_subscriptions(self) -> list[Subscription]:
        keys = await self.redis.keys(f"{_prefix_subscription}:*")
        subscriptions: list[Subscription] = []

        for key in keys:
            result = await self.redis.get(key)
            if result is None:
                continue
            subscriptions.append(Subscription.model_validate_json(result))

        return subscriptions

    async def _notify_location(
        self,
        subscription: Subscription,
        location: GeographicalCoordinates,
        *,
        endpoint: Optional[str] = None,
    ) -> bool:
        """Returns bool indicating whether the subscription was deleted or not."""
        device_location = geopy.Point(latitude=location.lat, longitude=location.lon)

        geofencing_area = subscription.config.subscriptionDetail.area
        center = geopy.Point(
            latitude=geofencing_area.center.latitude,
            longitude=geofencing_area.center.longitude,
        )

        radius = geofencing_area.radius
        distance = geopy.distance.geodesic(center, device_location).m

        notified = False

        if distance < radius:
            notified = await self._handle_inside_area(subscription)
        elif distance > radius:
            notified = await self._handle_outside_area(subscription)

        if notified:
            key = f"{_prefix_counter}:{subscription.id}"
            res = await self.redis.get(key)
            counter = 0 if res is None else int(res)
            counter += 1
            if counter == subscription.config.subscriptionMaxEvents:
                await self.delete_subscription(
                    subscription.id,
                    endpoint=endpoint,
                    termination_reason=TerminationReason.MAX_EVENTS_REACHED,
                )
                return True
            await self.redis.set(key, counter)
        return False

    async def _handle_inside_area(self, subscription: Subscription) -> bool:
        LOG.debug("Device inside area")

        key = f"{_prefix_last_state}:{subscription.id}"
        last_state = await self.redis.get(key)

        if last_state is None and not subscription.config.initialEvent:
            await self.redis.set(key, State.INSIDE)
            return False

        if last_state == State.INSIDE:
            return False

        await self.redis.set(key, State.INSIDE)

        if subscription.types[0] != SubscriptionEventType.v0_area_entered:
            return False

        res = CloudEvent(
            id=subscription.id,
            source=settings.geofencing.geofencing_url.unicode_string(),
            type=NotificationEventType.v0_area_entered,
            time=datetime.now(
                timezone.utc
                if subscription.config.subscriptionExpireTime is None
                else subscription.config.subscriptionExpireTime.tzinfo
            ),
            data=AreaEntered(
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=subscription.id,
            ),
        )

        await self.httpx_client.post(
            subscription.sink,
            content=res.model_dump_json(),
            headers={"Content-Type": "application/json"},
        )
        return True

    async def _handle_outside_area(self, subscription: Subscription) -> bool:
        LOG.debug("Device oustide area")

        key = f"{_prefix_last_state}:{subscription.id}"
        last_state = await self.redis.get(key)

        if last_state is None and not subscription.config.initialEvent:
            await self.redis.set(key, State.OUTSIDE)
            return False

        if last_state == State.OUTSIDE:
            return False

        await self.redis.set(key, State.OUTSIDE)

        if subscription.types[0] != SubscriptionEventType.v0_area_left:
            return False

        res = CloudEvent(
            id=subscription.id,
            source=settings.geofencing.geofencing_url.unicode_string(),
            type=NotificationEventType.v0_area_left,
            time=datetime.now(
                timezone.utc
                if subscription.config.subscriptionExpireTime is None
                else subscription.config.subscriptionExpireTime.tzinfo
            ),
            data=AreaLeft(
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=subscription.id,
            ),
        )

        await self.httpx_client.post(subscription.sink, content=res.model_dump_json())
        return True
