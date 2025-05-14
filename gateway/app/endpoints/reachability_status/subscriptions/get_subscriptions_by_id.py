from fastapi import APIRouter

from app.schemas.reachability_status import Subscription
from app.drivers.reachability_status import ReachabilityStatusInterfaceDep

router = APIRouter()


@router.get("/subscriptions/{subscriptionId}")
async def get_subscriptions_by_id(
    subscriptionId: str,
    reachability_status_subscription_interface: ReachabilityStatusInterfaceDep,
) -> Subscription:
    return await reachability_status_subscription_interface.get_subscription(
        subscriptionId
    )
