from datetime import datetime
from enum import Enum
import logging
import geopy
import geopy.distance
import httpx
from pydantic import AnyUrl
from app.redis import get_redis
from app.settings import settings
from app.interfaces.geofencing_subscriptions import (
    GeofencingSubscriptionInterface,
    GeofencingSubscriptionNotFound,
)
from app.schemas.geofencing import (
    AreaEntered,
    AreaLeft,
    CloudEvent,
    GeographicalCoordinates,
    MonitoringEventSubscription,
    MonitoringEventSubscriptionCreate,
    MonitoringType,
    NotificationEventType,
    Protocol,
    Status,
    Subscription,
    SubscriptionEventType,
    SubscriptionRequest,
)

LOG = logging.getLogger(__name__)

_prefix = "geofencing"
_prefix_last_state = "geofencing_state"
_webhook_url = AnyUrl("http://host.docker.internal:8000/geofencing/webhook")

_temp_auth = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQyMjQ4MzYsInN1YiI6IjEifQ.-POD0O20f6fe720oGdYKs9AbwhW7KbF5GQ-Sc_nUyug"


class State(str, Enum):
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


class RedisGeofencingSubscriptionInterface(GeofencingSubscriptionInterface):

    def __init__(self) -> None:
        super().__init__()
        self.httpx_client = httpx.AsyncClient()

    async def create_location_retrieval_subscription(
        self, req: SubscriptionRequest
    ) -> Subscription:
        device = req.config.subscriptionDetail.device
        body = MonitoringEventSubscriptionCreate(
            externalId=device.networkAccessIdentifier,
            notificationDestination=_webhook_url,
            monitoringType=MonitoringType.LOCATION_REPORTING,
            # Temporary solution
            maximumNumberOfReports=99999,
            monitorExpireTime=req.config.subscriptionExpireTime,
        )

        print(body.model_dump_json())

        res = await self.httpx_client.post(
            f"{settings.geofencing.monitoring_url}/subscriptions",
            content=body.model_dump_json(),
            headers={"Authorization": _temp_auth},
        )
        print(res.content)

        subscription_result = MonitoringEventSubscription.model_validate_json(
            res.content
        )

        res = Subscription(
            protocol=Protocol.HTTP,
            sink=req.sink,
            types=req.types,
            config=req.config,
            startsAt=datetime.now(),
            id=self._get_subscription_id_from_subscription_url(
                subscription_result.link
            ),
            expiresAt=subscription_result.monitorExpireTime,
            status=Status.ACTIVE,
        )

        return res

    def _get_subscription_id_from_subscription_url(self, url: AnyUrl | None) -> str:
        if url is None or url.path is None:
            raise Exception("Invalid url")

        return url.path.rsplit("/")[-1]

    async def store_subscription(self, subscription: Subscription) -> None:
        redis = get_redis()

        key = f"{_prefix}:{subscription.id}"

        await redis.set(key, subscription.model_dump_json())
        if subscription.expiresAt is not None:
            await redis.expireat(key, subscription.expiresAt)

    async def delete_subscription(self, id: str) -> None:
        redis = get_redis()

        key = f"{_prefix}:{id}"
        last_state_key = f"{_prefix_last_state}:{id}"

        subscription = await redis.get(key)
        if subscription is None:
            raise GeofencingSubscriptionNotFound()

        await self.httpx_client.delete(
            f"{settings.geofencing.monitoring_url}/subscriptions/{id}",
            headers={"Authorization": _temp_auth},
        )

        await redis.delete(key)
        await redis.delete(last_state_key)

    async def get_subscription(self, id: str) -> Subscription:
        redis = get_redis()

        key = f"{_prefix}:{id}"

        result = await redis.get(key)

        if result is None:
            raise GeofencingSubscriptionNotFound()

        return Subscription.model_validate_json(result)

    async def get_subscriptions(self) -> list[Subscription]:
        redis = get_redis()

        keys = await redis.keys(f"{_prefix}:*")
        subscriptions: list[Subscription] = []

        for key in keys:
            result = await redis.get(key)
            if result is None:
                continue

            subscriptions.append(Subscription.model_validate_json(result))

        return subscriptions

    async def notify_location(
        self, subscription: Subscription, location: GeographicalCoordinates
    ) -> None:
        device_location = geopy.Point(latitude=location.lat, longitude=location.lon)

        geofencing_area = subscription.config.subscriptionDetail.area
        center = geopy.Point(
            latitude=geofencing_area.center.latitude.root,
            longitude=geofencing_area.center.longitude.root,
        )

        radius = geofencing_area.radius
        distance = geopy.distance.geodesic(center, device_location).m

        if distance < radius:
            await self._handle_inside_area(subscription)

        if distance > radius:
            await self._handle_outside_area(subscription)

    async def _handle_inside_area(self, subscription: Subscription):
        LOG.debug("Device inside area")

        redis = get_redis()
        key = f"{_prefix_last_state}:{subscription.id}"
        last_state = await redis.get(key)

        print(last_state)
        if last_state is None:
            await redis.set(key, State.INSIDE)
            return

        if last_state == State.INSIDE:
            return

        await redis.set(key, State.INSIDE)

        if (
            subscription.types[0]
            != SubscriptionEventType.org_camaraproject_geofencing_subscriptions_v0_area_entered
        ):
            return

        res = CloudEvent(
            id=subscription.id,
            # TODO: change this
            source="idk",
            type=NotificationEventType.org_camaraproject_geofencing_subscriptions_v0_area_entered,
            time=datetime.now(),
            data=AreaEntered(
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=subscription.id,
            ).model_dump(),
        )

        print("sending")
        await self.httpx_client.post(
            subscription.sink,
            content=res.model_dump_json(),
            headers={"Content-Type": "application/json"},
        )

    async def _handle_outside_area(self, subscription: Subscription):
        LOG.debug("Device oustide area")

        redis = get_redis()
        key = f"{_prefix_last_state}:{subscription.id}"
        last_state = await redis.get(key)

        print(last_state)
        if last_state is None:
            await redis.set(key, State.OUTSIDE)
            return

        if last_state == State.OUTSIDE:
            return

        await redis.set(key, State.OUTSIDE)

        if (
            subscription.types[0]
            != SubscriptionEventType.org_camaraproject_geofencing_subscriptions_v0_area_left
        ):
            return
        res = CloudEvent(
            id=subscription.id,
            source="idk",
            type=NotificationEventType.org_camaraproject_geofencing_subscriptions_v0_area_left,
            time=datetime.now(),
            data=AreaLeft(
                device=subscription.config.subscriptionDetail.device,
                area=subscription.config.subscriptionDetail.area,
                subscriptionId=subscription.id,
            ).model_dump(),
        )

        print("sending")
        await self.httpx_client.post(subscription.sink, content=res.model_dump_json())
