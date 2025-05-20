from fastapi import APIRouter

from app.schemas.roaming_status import Subscription
from app.drivers.roaming_status import RoamingStatusSubscriptionInterfaceDep

router = APIRouter()


@router.get("/subscriptions/{subscriptionId}", response_model_exclude_unset=True)
async def get_subscriptions_by_id(
    subscriptionId: str,
    roaming_status_subscription_interface: RoamingStatusSubscriptionInterfaceDep,
) -> Subscription:
    return await roaming_status_subscription_interface.get_subscription(subscriptionId)
