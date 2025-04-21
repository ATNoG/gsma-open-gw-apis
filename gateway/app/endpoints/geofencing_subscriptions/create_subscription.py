from fastapi import APIRouter

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.schemas.geofencing import Subscription, SubscriptionRequest

router = APIRouter()


@router.post("/subscriptions")
async def post_subscriptions(
    req: SubscriptionRequest,
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> Subscription:
    await geofencing_subscription_interface.clear_expired_subscriptions()
    subscription = (
        await geofencing_subscription_interface.create_location_retrieval_subscription(
            req
        )
    )
    await geofencing_subscription_interface.store_subscription(subscription)
    return subscription
