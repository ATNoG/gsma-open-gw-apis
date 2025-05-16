from abc import ABC, abstractmethod

from app.schemas.device import Device
from app.schemas.reachability_status import (
    ReachabilityStatusResponse,
    Subscription,
    SubscriptionRequest,
)


class ReachabilityStatusInterface(ABC):
    @abstractmethod
    async def get_reachability_status(
        self, device: Device
    ) -> ReachabilityStatusResponse:
        pass

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
