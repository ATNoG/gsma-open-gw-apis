from abc import ABC, abstractmethod

from app.schemas.geofencing import (
    GeographicalCoordinates,
    Subscription,
    SubscriptionRequest,
)


class GeofencingSubscriptionNotFound(Exception):
    pass


class GeofencingSubscriptionInterface(ABC):
    @abstractmethod
    async def create_location_retrieval_subscription(
        self, req: SubscriptionRequest
    ) -> Subscription:
        pass

    @abstractmethod
    async def store_subscription(self, subscription: Subscription) -> None:
        pass

    @abstractmethod
    async def delete_subscription(self, id: str) -> None:
        pass

    @abstractmethod
    async def get_subscription(self, id: str) -> Subscription:
        pass

    @abstractmethod
    async def get_subscriptions(self) -> list[Subscription]:
        pass

    @abstractmethod
    async def notify_location(
        self, subscription: Subscription, location: GeographicalCoordinates
    ) -> bool:
        """Returns bool indicating whether the subscription was deleted or not."""
        pass

    @abstractmethod
    async def clear_expired_subscriptions(self) -> None:
        pass

    @abstractmethod
    async def queue_notification(
        self, subscription_id: str, location: GeographicalCoordinates
    ) -> None:
        pass
