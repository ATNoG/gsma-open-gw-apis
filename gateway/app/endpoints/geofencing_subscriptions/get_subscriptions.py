from fastapi import APIRouter

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.schemas.geofencing import Subscription

router = APIRouter()


@router.get("/subscriptions")
async def get_subscription(
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> list[Subscription]:
    await geofencing_subscription_interface.clear_expired_subscriptions()
    return await geofencing_subscription_interface.get_subscriptions()
