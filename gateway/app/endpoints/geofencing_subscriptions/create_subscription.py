from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body

from app.drivers.geofencing import GeofencingSubscriptionInterfaceDep
from app.exceptions import ApiException, MissingDevice
from app.schemas.geofencing import Subscription, SubscriptionRequest
from app.schemas.subscriptions import Protocol

router = APIRouter()


@router.post("/subscriptions", response_model_exclude_unset=True)
async def post_subscriptions(
    req: Annotated[SubscriptionRequest, Body()],
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
