from abc import ABC, abstractmethod

from app.schemas.device import Device
from app.schemas.roaming_status import (
    RoamingStatusResponse,
    Subscription,
    SubscriptionRequest,
)


class RoamingStatusInterface(ABC):
    @abstractmethod
    async def get_roaming_status(self, device: Device) -> RoamingStatusResponse:
        pass


class RoamingStatusSubscriptionInterface(ABC):
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
