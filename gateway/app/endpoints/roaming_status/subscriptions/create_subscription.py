from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body

from app.exceptions import ApiException, MissingDevice, UnsupportedIdentifier
from app.schemas.subscriptions import Protocol
from app.schemas.roaming_status import Subscription, SubscriptionRequest
from app.drivers.roaming_status import RoamingStatusSubscriptionInterfaceDep

router = APIRouter()


@router.post("/subscriptions", response_model_exclude_unset=True)
async def post_subscriptions(
    req: Annotated[SubscriptionRequest, Body()],
    roaming_status_subscription_interface: RoamingStatusSubscriptionInterfaceDep,
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
        raise UnsupportedIdentifier()

    return await roaming_status_subscription_interface.create_subscription(req, device)
