import asyncio
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Never, Optional, Union

import geopy
import geopy.distance
import httpx
from fastapi.encoders import jsonable_encoder
from pydantic import AnyHttpUrl, AnyUrl

from app.exceptions import ResourceNotFound
from app.drivers.nef_auth import NEFAuth
from app.exceptions import ApiException
from app.interfaces.geofencing_subscriptions import (
    GeofencingSubscriptionInterface,
)
from app.redis import get_redis
from app.schemas.device import Device
from app.schemas.geofencing import (
    AreaEntered,
    AreaLeft,
    CloudEvent,
    NotificationEventType,
    Subscription,
    SubscriptionEventType,
    SubscriptionRequest,
    SubscriptionTypeAdapter,
    SubscriptionEnds,
)
from app.schemas.subscriptions import (
    HTTPSubscriptionResponse,
    Protocol,
    SubscriptionStatus,
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


class State(Enum):
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


def _handle_post_error(res: httpx.Response) -> None:
    raise ApiException(
        message="Error comunicating with the core",
    )


_termination_reason_to_status = {
    TerminationReason.SUBSCRIPTION_DELETED: SubscriptionStatus.DELETED,
    TerminationReason.SUBSCRIPTION_EXPIRED: SubscriptionStatus.EXPIRED,
    TerminationReason.MAX_EVENTS_REACHED: SubscriptionStatus.EXPIRED,
}

_handle_state_details: dict[
    State,
    tuple[
        SubscriptionEventType, NotificationEventType, type[Union[AreaEntered, AreaLeft]]
    ],
] = {
    State.INSIDE: (
        SubscriptionEventType.v0_area_entered,
        NotificationEventType.v0_area_entered,
        AreaEntered,
    ),
    State.OUTSIDE: (
        SubscriptionEventType.v0_area_left,
        NotificationEventType.v0_area_left,
        AreaLeft,
    ),
}


class NefGeofencingSubscriptionInterface(GeofencingSubscriptionInterface):
    def __init__(self, nef_url: AnyHttpUrl, nef_auth: NEFAuth) -> None:
        super().__init__()
        self.httpx_client = httpx.AsyncClient(base_url=str(nef_url), auth=nef_auth)
        self.httpx_client_callback = httpx.AsyncClient()
        self.redis = get_redis()

    async def _clear_loop(self) -> Never:
        while True:
            try:
                LOG.debug("Clearing expired subscriptions")
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
        await self.redis.set(sub_key, sub.model_dump_json())

        # Create monitoring event subscription
        body = MonitoringEventSubscription(
            ipv6Addr=device.ipv6Address,
            notificationDestination=AnyUrl(
                f"{settings.nef_gateway_url}callbacks/v1/geofencing/{sub_id}"
            ),
            monitoringType=MonitoringType.LOCATION_REPORTING,
            monitorExpireTime=req.config.subscriptionExpireTime or datetime.max,
            immediateRep=req.config.initialEvent,
        )

        if device.phoneNumber is not None:
            body.msisdn = device.phoneNumber[1:]

        if device.ipv4Address is not None:
            body.ipv4Addr = device.ipv4Address.publicAddress

        res = await self.httpx_client.post(
            f"{settings.geofencing.monitoring_base_path}/subscriptions",
            json=jsonable_encoder(body),
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

    async def delete_subscription(
        self,
        sub_id: str,
        *,
        endpoint: Optional[str] = None,
        termination_reason: TerminationReason = TerminationReason.SUBSCRIPTION_DELETED,
    ) -> None:
        subscription_key = f"{_prefix_subscription}:{sub_id}"
        last_state_key = f"{_prefix_last_state}:{sub_id}"
        counter_key = f"{_prefix_counter}:{sub_id}"
        nef_url_key = f"{_prefix_nef_url}:{sub_id}"

        subscription = await self.redis.get(subscription_key)
        if subscription is None:
            raise ResourceNotFound()

        nef_subscription_url: str
        if endpoint is None:
            nef_subscription_url = await self.redis.get(nef_url_key)
        else:
            nef_subscription_url = endpoint

        await self.httpx_client.delete(nef_subscription_url)

        await self.redis.delete(last_state_key, counter_key, nef_url_key)

        subscription = SubscriptionTypeAdapter.validate_json(subscription)
        subscription.status = _termination_reason_to_status[termination_reason]
        await self.redis.set(subscription_key, subscription.model_dump_json())

        res = CloudEvent(
            id=str(uuid.uuid4()),
            source=f"{settings.gateway_url}geofencing-subscriptions/v0.4/{sub_id}",
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
                subscriptionId=sub_id,
            ),
        )

        await self.httpx_client_callback.post(
            subscription.sink,
            json=jsonable_encoder(res),
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
            notified = await self._handle_area(subscription, State.INSIDE)
        elif distance > radius:
            notified = await self._handle_area(subscription, State.OUTSIDE)

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

    async def _handle_area(self, subscription: Subscription, state: State) -> bool:
        LOG.debug("Device %s area", state)

        key = f"{_prefix_last_state}:{subscription.id}"
        last_state = await self.redis.get(key)

        if last_state is None and not subscription.config.initialEvent:
            await self.redis.set(key, state.value)
            return False

        if last_state == state.value:
            return False

        await self.redis.set(key, state.value)

        sub_event_type, notif_event_type, notif_data_class = _handle_state_details[
            state
        ]

        if sub_event_type not in subscription.types:
            return False

        res = CloudEvent(
            id=str(uuid.uuid4()),
            source=f"{settings.gateway_url}geofencing-subscriptions/v0.4/{subscription.id}",
            type=notif_event_type,
            time=datetime.now(
                timezone.utc
                if subscription.config.subscriptionExpireTime is None
                else subscription.config.subscriptionExpireTime.tzinfo
            ),
            data=notif_data_class(
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=subscription.id,
            ),
        )

        await self.httpx_client_callback.post(
            subscription.sink, json=jsonable_encoder(res)
        )
        return True
