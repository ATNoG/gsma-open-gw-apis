from http import HTTPStatus

from fastapi import APIRouter

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep

router = APIRouter()


@router.delete("/subscriptions/{subscriptionId}", status_code=HTTPStatus.NO_CONTENT)
async def delete_subscriptions_by_id(
    subscriptionId: str,
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> None:
    await geofencing_subscription_interface.delete_subscription(subscriptionId)
