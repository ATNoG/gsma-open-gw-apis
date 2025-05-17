from fastapi import APIRouter

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.schemas.geofencing import Subscription

router = APIRouter()


@router.get("/subscriptions", response_model_exclude_unset=True)
async def get_subscription(
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> list[Subscription]:
    return await geofencing_subscription_interface.get_subscriptions()
