from fastapi import APIRouter

from app.schemas.reachability_status import Subscription
from app.drivers.reachability_status import ReachabilityStatusInterfaceDep

router = APIRouter()


@router.get("/subscriptions", response_model_exclude_unset=True)
async def get_subscription(
    reachability_status_subscription_interface: ReachabilityStatusInterfaceDep,
) -> list[Subscription]:
    return await reachability_status_subscription_interface.get_subscriptions()
