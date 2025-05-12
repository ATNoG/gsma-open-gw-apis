from fastapi import APIRouter

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.schemas.geofencing import Subscription, SubscriptionRequest

router = APIRouter()


@router.post("/subscriptions")
async def post_subscriptions(
    req: SubscriptionRequest,
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> Subscription:
    device = req.config.subscriptionDetail.device
    subscription = await geofencing_subscription_interface.create_subscription(
        req, device
    )
    return subscription
