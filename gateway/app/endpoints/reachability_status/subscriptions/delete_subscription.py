from http import HTTPStatus

from fastapi import APIRouter

from app.drivers.reachability_status import ReachabilityStatusInterfaceDep

router = APIRouter()


@router.delete("/subscriptions/{subscriptionId}", status_code=HTTPStatus.NO_CONTENT)
async def delete_subscriptions_by_id(
    subscriptionId: str,
    reachability_status_subscription_interface: ReachabilityStatusInterfaceDep,
) -> None:
    await reachability_status_subscription_interface.delete_subscription(subscriptionId)
