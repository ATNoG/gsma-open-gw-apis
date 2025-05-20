from fastapi import APIRouter

from app.schemas.roaming_status import Subscription
from app.drivers.roaming_status import RoamingStatusSubscriptionInterfaceDep

router = APIRouter()


@router.get("/subscriptions", response_model_exclude_unset=True)
async def get_subscription(
    roaming_status_subscription_interface: RoamingStatusSubscriptionInterfaceDep,
) -> list[Subscription]:
    return await roaming_status_subscription_interface.get_subscriptions()
