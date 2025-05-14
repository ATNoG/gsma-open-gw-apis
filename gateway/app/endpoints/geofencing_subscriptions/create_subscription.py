from http import HTTPStatus

from fastapi import APIRouter

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.exceptions import ApiException
from app.interfaces.geofencing_subscriptions import MissingDevice
from app.schemas.geofencing import Protocol, Subscription, SubscriptionRequest

router = APIRouter()


@router.post("/subscriptions")
async def post_subscriptions(
    req: SubscriptionRequest,
    geofencing_subscription_interface: GeofencingSubscriptionInterfaceDep,
) -> Subscription:
    if req.protocol != Protocol.HTTP:
        raise ApiException(
            status=HTTPStatus.BAD_REQUEST,
            code="INVALID_PROTOCOL",
            message="Only HTTP is supported.",
        )

    device = req.config.subscriptionDetail.device
    if device is None:
        raise MissingDevice()

    if device.networkAccessIdentifier is not None:
        raise ApiException(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            code="UNSUPPORTED_IDENTIFIER",
            message="The identifier provided is not supported.",
        )
    return await geofencing_subscription_interface.create_subscription(req, device)
