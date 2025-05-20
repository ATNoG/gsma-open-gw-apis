from http import HTTPStatus

from fastapi import APIRouter

from app.drivers.roaming_status import RoamingStatusSubscriptionInterfaceDep

router = APIRouter()


@router.delete("/subscriptions/{subscriptionId}", status_code=HTTPStatus.NO_CONTENT)
async def delete_subscriptions_by_id(
    subscriptionId: str,
    roaming_status_subscription_interface: RoamingStatusSubscriptionInterfaceDep,
) -> None:
    await roaming_status_subscription_interface.delete_subscription(subscriptionId)
