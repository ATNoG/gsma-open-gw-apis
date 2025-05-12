import asyncio
import logging
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
    GeographicalCoordinates,
    MonitoringEventSubscription,
    MonitoringType,
    NotificationEventType,
    Protocol,
    Status,
    Subscription,
    SubscriptionEventType,
    SubscriptionRequest,
)
from app.settings import settings

LOG = logging.getLogger(__name__)

_prefix_subscription = "geofencing"
_prefix_last_state = "geofencing_state"
_prefix_counter = "geofencing_counter"
_prefix_queue = "geofencing_queue"
_prefix_nef_url = "geofencing_nef_url"


class State(str, Enum):
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


def _handle_post_error(res: httpx.Response) -> None:
    raise ApiException(
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        message="Error comunicating with the core",
        code="INTERNAL_SERVER_ERROR",
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
        keys = await self.redis.keys(f"{_prefix_subscription}:*")

        for key in keys:
            sub = await self.redis.get(key)
            if sub is None:
                continue

            sub = Subscription.model_validate_json(sub)
            if (
                sub.config.subscriptionExpireTime is None
                or datetime.now(sub.config.subscriptionExpireTime.tzinfo)
                < sub.config.subscriptionExpireTime
            ):
                continue

            await self.delete_subscription(sub.id)

    async def create_subscription(
        self, req: SubscriptionRequest, device: Device
    ) -> Subscription:
        if req.protocol != Protocol.HTTP:
            raise ApiException(
                status=HTTPStatus.BAD_REQUEST,
                code="INVALID_PROTOCOL",
                message="Only HTTP is supported.",
            )

        if device.phoneNumber is None:
            raise ApiException(
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
                code="UNSUPPORTED_IDENTIFIER",
                message="The identifier provided is not supported.",
            )

        number = device.phoneNumber[1:]

        body = MonitoringEventSubscription(
            msisdn=number,
            notificationDestination=AnyUrl(
                f"{settings.nef_gateway_url}callbacks/v1/geofencing"
            ),
            monitoringType=MonitoringType.LOCATION_REPORTING,
            monitorExpireTime=req.config.subscriptionExpireTime or datetime.max,
            immediateRep=req.config.initialEvent,
        )

        res = await self.httpx_client.post(
            f"{settings.geofencing.monitoring_base_path}/subscriptions",
            content=body.model_dump_json(),
        )

        if not res.is_success:
            _handle_post_error(res)

        subscription_result = MonitoringEventSubscription.model_validate_json(
            res.content
        )

        if subscription_result.self is None:
            raise Exception("No 'self' in monitoring subscription response")

        nef_sub_id = self._get_subscription_id_from_subscription_url(
            subscription_result.self
        )

        req.config.subscriptionDetail.device = device
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
            id=nef_sub_id,
            expiresAt=req.config.subscriptionExpireTime,
            status=Status.ACTIVE,
        )

        # Store subscription

        key = f"{_prefix_subscription}:{nef_sub_id}"
        queue_key = f"{_prefix_queue}:{nef_sub_id}"
        self_key = f"{_prefix_nef_url}:{nef_sub_id}"
        queued_locations = await self.redis.lrange(queue_key, 0, -1)  # type: ignore [misc]
        for location in queued_locations:
            location = GeographicalCoordinates.model_validate_json(location)
            if await self._notify_location(sub, location, pre_store=True):
                break
        else:
            await self.redis.set(key, sub.model_dump_json())
            await self.redis.set(self_key, subscription_result.self.unicode_string())

        await self.redis.delete(queue_key)

        return sub

    def _get_subscription_id_from_subscription_url(self, url: AnyUrl) -> str:
        if url.path is None:
            raise Exception("Invalid url")

        return url.path.rsplit("/")[-1]

    async def _queue_notification(
        self, subscription_id: str, location: GeographicalCoordinates
    ) -> None:
        await self.redis.rpush(
            f"{_prefix_queue}:{subscription_id}", location.model_dump_json()
        )  # type: ignore [misc]
        await self.redis.expire(f"{_prefix_queue}:{subscription_id}", 10, nx=True)

    async def delete_subscription(
        self, id: str, *, pre_store_sub: Optional[Subscription] = None
    ) -> None:
        subscription_key = f"{_prefix_subscription}:{id}"
        last_state_key = f"{_prefix_last_state}:{id}"
        counter_key = f"{_prefix_counter}:{id}"
        url_key = f"{_prefix_nef_url}:{id}"

        subscription = await self.redis.get(subscription_key)
        if pre_store_sub is None and subscription is None:
            raise GeofencingSubscriptionNotFound()

        url = await self.redis.get(url_key)

        await self.httpx_client.delete(url)

        await self.redis.delete(subscription_key)
        await self.redis.delete(last_state_key)
        await self.redis.delete(counter_key)
        await self.redis.delete(url_key)

        subscription = (
            Subscription.model_validate_json(subscription)
            if pre_store_sub is None
            else pre_store_sub
        )

        res = CloudEvent(
            id=subscription.id,
            source=settings.geofencing.geofencing_url.unicode_string(),
            type=NotificationEventType.v0_subscription_ends,
            time=datetime.now(
                timezone.utc
                if subscription.config.subscriptionExpireTime is None
                else subscription.config.subscriptionExpireTime.tzinfo
            ),
            data=AreaEntered(
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=subscription.id,
            ).model_dump(),
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
        pre_store: bool = False,
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
                    subscription.id, pre_store_sub=subscription if pre_store else None
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
            ).model_dump(),
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
            ).model_dump(),
        )

        await self.httpx_client.post(subscription.sink, content=res.model_dump_json())
        return True
