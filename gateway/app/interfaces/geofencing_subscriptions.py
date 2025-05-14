from abc import ABC, abstractmethod

from app.schemas.device import Device
from app.schemas.geofencing import Subscription, SubscriptionRequest


class GeofencingSubscriptionNotFound(Exception):
    pass


class GeofencingSubscriptionInterface(ABC):
    @abstractmethod
    async def create_subscription(
        self, req: SubscriptionRequest, device: Device
    ) -> Subscription:
        pass

    @abstractmethod
    async def delete_subscription(self, sub_id: str) -> None:
        pass

    @abstractmethod
    async def get_subscription(self, sub_id: str) -> Subscription:
        pass

    @abstractmethod
    async def get_subscriptions(self) -> list[Subscription]:
        pass
