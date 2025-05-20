import uuid
import asyncio
import logging
from typing import Any, Never
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from pydantic import TypeAdapter


from app.exceptions import ResourceNotFound
from app.redis import get_redis
from app.schemas.subscriptions import (
    HTTPSubscriptionResponse,
    Protocol,
    Subscription,
    SubscriptionRequest,
    SubscriptionStatus,
    TerminationReason,
)
from app.utils.subscription_driver_base import SubscriptionDriverBase

_termination_reason_to_status = {
    TerminationReason.SUBSCRIPTION_DELETED: SubscriptionStatus.DELETED,
    TerminationReason.SUBSCRIPTION_EXPIRED: SubscriptionStatus.EXPIRED,
    TerminationReason.MAX_EVENTS_REACHED: SubscriptionStatus.EXPIRED,
}


class SubscriptionDriverRedis[
    SubscriptionEventType: str,
    SubscriptionDetails,
    NotificationEventType: str,
    CloudEventData,
](ABC, SubscriptionDriverBase[NotificationEventType, CloudEventData]):
    def __init__(
        self,
        source: str,
        prefix: str,
        type_adapter: TypeAdapter[
            Subscription[SubscriptionEventType, SubscriptionDetails]
        ],
    ) -> None:
        super().__init__(source)

        self.sub_prefix = prefix
        self.counter_prefix = prefix + "_counter"

        self.type_adapter = type_adapter

        self.redis = get_redis()

    async def create_gateway_subscription(
        self,
        req: SubscriptionRequest[SubscriptionEventType, SubscriptionDetails],
    ) -> Subscription[SubscriptionEventType, SubscriptionDetails]:
        sub_id = str(uuid.uuid4())
        sub: Subscription[SubscriptionEventType, SubscriptionDetails] = (
            HTTPSubscriptionResponse(
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
        )

        await self.redis.set(
            f"{self.sub_prefix}:{sub_id}", sub.model_dump_json(exclude_unset=True)
        )

        return sub

    async def permanently_delete_subscription(
        self, sub: Subscription[SubscriptionEventType, SubscriptionDetails]
    ) -> None:
        await self.redis.delete(f"{self.sub_prefix}:{sub.id}")

    async def delete_gateway_subscription(
        self, id: str, termination_reason: TerminationReason
    ) -> Subscription[SubscriptionEventType, SubscriptionDetails] | None:
        subscription_key = f"{self.sub_prefix}:{id}"
        subscription_raw = await self.redis.get(subscription_key)
        if subscription_raw is None:
            raise ResourceNotFound()

        # Delete all the redis data besides the subscription
        counter_key = f"{self.counter_prefix}:{id}"
        await self.redis.delete(counter_key)

        subscription = self.type_adapter.validate_json(subscription_raw)

        if subscription.status in (
            SubscriptionStatus.EXPIRED,
            SubscriptionStatus.DELETED,
        ):
            return None

        subscription.status = _termination_reason_to_status[termination_reason]
        await self.redis.set(
            subscription_key, subscription.model_dump_json(exclude_unset=True)
        )

        return subscription

    @abstractmethod
    async def delete_subscription(
        self,
        sub_id: str,
        *,
        termination_reason: TerminationReason,
    ) -> None:
        pass

    async def get_subscription(
        self, sub_id: str
    ) -> Subscription[SubscriptionEventType, SubscriptionDetails]:
        result = await self.redis.get(f"{self.sub_prefix}:{sub_id}")

        if result is None:
            raise ResourceNotFound()

        return self.type_adapter.validate_json(result)

    async def get_subscriptions(
        self,
    ) -> list[Subscription[SubscriptionEventType, SubscriptionDetails]]:
        keys = await self.redis.keys(f"{self.sub_prefix}:*")
        subscriptions = []

        for key in keys:
            result = await self.redis.get(key)
            if result is None:
                continue
            subscriptions.append(self.type_adapter.validate_json(result))

        return subscriptions

    async def send_report(
        self,
        subscription: Subscription[SubscriptionEventType, SubscriptionDetails],
        type: NotificationEventType,
        data: CloudEventData,
        **delete_kwargs: Any,
    ) -> None:
        if subscription.config.subscriptionMaxEvents is not None:
            counter_key = f"{self.counter_prefix}:{subscription.id}"
            counter = await self.redis.incr(counter_key)

            if counter >= subscription.config.subscriptionMaxEvents:
                await self.delete_subscription(
                    subscription.id,
                    termination_reason=TerminationReason.MAX_EVENTS_REACHED,
                    **delete_kwargs,
                )

        await self.notify_sink(subscription, type, data)

    async def clear_loop(self) -> Never:
        while True:
            try:
                logging.debug("Clearing expired subscriptions")
                await self._clear_expired_subscriptions()
                await asyncio.sleep(5)
            except Exception as e:
                logging.error(e)

    async def _clear_expired_subscriptions(self) -> None:
        keys = await self.redis.keys(f"{self.sub_prefix}:*")

        for key in keys:
            sub_key = f"{self.sub_prefix}:{key.split(':')[1]}"
            sub = await self.redis.get(sub_key)
            if sub is None:
                continue

            sub = self.type_adapter.validate_json(sub)
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
