from fastapi import APIRouter, Response
from http import HTTPStatus

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep


router = APIRouter()


@router.delete("/subscriptions/{subscriptionId}")
async def delete_subscriptions_by_id(
    subscriptionId: str,
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> Response:
    await geofencing_subscription_interface.delete_subscription(subscriptionId)
    return Response(status_code=HTTPStatus.NO_CONTENT.value)
