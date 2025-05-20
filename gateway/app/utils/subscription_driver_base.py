import uuid
import asyncio
from datetime import datetime, timezone

import httpx
from fastapi.encoders import jsonable_encoder

from app.schemas.subscriptions import CloudEvent, Subscription


class SubscriptionDriverBase[NotificationEventType: str, CloudEventData]:
    def __init__(self, source: str) -> None:
        super().__init__()

        self.httpx_client_callback = httpx.AsyncClient()

        self.source = source

    def send_cloud_event(
        self, sink: str, event: CloudEvent[NotificationEventType, CloudEventData]
    ) -> None:
        asyncio.create_task(
            self.httpx_client_callback.post(
                sink,
                json=jsonable_encoder(event, exclude_unset=True),
            )
        )

    async def notify_sink[SubscriptionEventType: str, SubscriptionDetail](
        self,
        subscription: Subscription[SubscriptionEventType, SubscriptionDetail],
        type: NotificationEventType,
        data: CloudEventData,
    ) -> None:
        res: CloudEvent[NotificationEventType, CloudEventData] = CloudEvent(
            id=str(uuid.uuid4()),
            source=self.source,
            type=type,
            time=datetime.now(
                timezone.utc
                if subscription.config.subscriptionExpireTime is None
                else subscription.config.subscriptionExpireTime.tzinfo
            ),
            data=data,
        )

        self.send_cloud_event(subscription.sink, res)
