from fastapi import APIRouter

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.schemas.geofencing import Subscription

router = APIRouter()


@router.get("/subscriptions/{subscriptionId}")
async def get_subscriptions_by_id(
    subscriptionId: str,
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> Subscription:
    await geofencing_subscription_interface.clear_expired_subscriptions()
    return await geofencing_subscription_interface.get_subscription(subscriptionId)
