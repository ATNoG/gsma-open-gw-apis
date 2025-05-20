import logging
import asyncio
from enum import Enum
from typing import Optional, Union
from datetime import datetime

import geopy
import geopy.distance
from fastapi.encoders import jsonable_encoder
from pydantic import AnyUrl

from app.exceptions import ApiException
from app.interfaces.geofencing_subscriptions import (
    GeofencingSubscriptionInterface,
)
from app.schemas.device import Device
from app.schemas.geofencing import (
    AreaEntered,
    AreaLeft,
    CloudEventData,
    NotificationEventType,
    Subscription,
    SubscriptionDetail,
    SubscriptionEventType,
    SubscriptionRequest,
    SubscriptionTypeAdapter,
    SubscriptionEnds,
)
from app.schemas.subscriptions import (
    TerminationReason,
)
from app.schemas.nef_schemas.monitoringevent import (
    GeographicalCoordinates,
    MonitoringEventSubscription,
    MonitoringType,
)
from app.settings import NEFSettings
from app.utils.nef_driver_base import NefDriverBase
from app.utils.subscription_driver_redis import SubscriptionDriverRedis

LOG = logging.getLogger(__name__)

_prefix_last_state = "geofencing_state"
_prefix_nef_url = "geofencing_nef_url"


class State(Enum):
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


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


class NefGeofencingSubscriptionInterface(
    GeofencingSubscriptionInterface,
    NefDriverBase,
    SubscriptionDriverRedis[
        SubscriptionEventType,
        SubscriptionDetail,
        NotificationEventType,
        CloudEventData,
    ],
):
    def __init__(self, nef_settings: NEFSettings, source: str) -> None:
        NefDriverBase.__init__(self, nef_settings)
        SubscriptionDriverRedis.__init__(
            self, source, "geofencing", SubscriptionTypeAdapter
        )

        self.notification_url = nef_settings.get_notification_url()

    async def create_subscription(
        self, req: SubscriptionRequest, device: Device
    ) -> Subscription:
        # Store subscription
        req.config.subscriptionDetail.device = device
        sub = await self.create_gateway_subscription(req)

        try:
            # Create monitoring event subscription
            body = MonitoringEventSubscription(
                ipv6Addr=device.ipv6Address,
                notificationDestination=AnyUrl(
                    f"{self.notification_url}/callbacks/v1/geofencing/{sub.id}"
                ),
                monitoringType=MonitoringType.LOCATION_REPORTING,
                monitorExpireTime=req.config.subscriptionExpireTime or datetime.max,
                immediateRep=req.config.initialEvent,
            )

            body = self.install_device_identifiers(body, device)

            res = await self.httpx_client.post(
                f"/3gpp-monitoring-event/v1/{self.af_id}/subscriptions",
                json=jsonable_encoder(body),
            )

            # Check success of monitoring event subscription
            if not res.is_success:
                raise ApiException(
                    message="Error comunicating with the core",
                )

            subscription_result = MonitoringEventSubscription.model_validate_json(
                res.content
            )

            if subscription_result.self is None:
                LOG.error("No 'self' in monitoring subscription response")
                raise ApiException(
                    message="Error comunicating with the core",
                )

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

        last_state_key = f"{_prefix_last_state}:{sub_id}"
        nef_url_key = f"{_prefix_nef_url}:{sub_id}"

        if nef_subscription_url is None:
            nef_subscription_url = await self.redis.get(nef_url_key)

        if nef_subscription_url is not None:
            # Schedule the deletion of the NEF subscription
            asyncio.create_task(self.delete_nef_subscription(nef_subscription_url))

        await self.redis.delete(last_state_key, nef_url_key)

        await self.notify_sink(
            subscription,
            NotificationEventType.v0_subscription_ends,
            SubscriptionEnds(
                terminationReason=termination_reason,
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=sub_id,
            ),
        )

    async def get_subscription(self, sub_id: str) -> Subscription:
        return await SubscriptionDriverRedis.get_subscription(self, sub_id)

    async def get_subscriptions(self) -> list[Subscription]:
        return await SubscriptionDriverRedis.get_subscriptions(self)

    async def notify_location(
        self,
        subscription: Subscription,
        location: GeographicalCoordinates,
        *,
        nef_subscription_url: Optional[str] = None,
    ) -> None:
        """Returns bool indicating whether the subscription was deleted or not."""
        device_location = geopy.Point(latitude=location.lat, longitude=location.lon)

        geofencing_area = subscription.config.subscriptionDetail.area
        center = geopy.Point(
            latitude=geofencing_area.center.latitude,
            longitude=geofencing_area.center.longitude,
        )

        radius = geofencing_area.radius
        distance = geopy.distance.geodesic(center, device_location).m

        state: State
        if distance < radius:
            state = State.INSIDE
        elif distance > radius:
            state = State.OUTSIDE
        else:
            return

        await self._handle_area(subscription, state, nef_subscription_url)

    async def _handle_area(
        self,
        subscription: Subscription,
        state: State,
        nef_subscription_url: Optional[str],
    ) -> None:
        LOG.debug("Device %s area", state)

        key = f"{_prefix_last_state}:{subscription.id}"
        last_state = await self.redis.get(key)

        if last_state == state.value:
            return

        await self.redis.set(key, state.value)

        if last_state is None and not subscription.config.initialEvent:
            return

        sub_event_type, notif_event_type, notif_data_class = _handle_state_details[
            state
        ]

        if sub_event_type not in subscription.types:
            return

        await self.send_report(
            subscription,
            notif_event_type,
            notif_data_class(
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=subscription.id,
            ),
            nef_subscription_url=nef_subscription_url,
        )
