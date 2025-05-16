from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body

from app.exceptions import ApiException, MissingDevice, UnsupportedIdentifier
from app.schemas.subscriptions import Protocol
from app.schemas.reachability_status import Subscription, SubscriptionRequest
from app.drivers.reachability_status import ReachabilityStatusInterfaceDep

router = APIRouter()


@router.post("/subscriptions")
async def post_subscriptions(
    req: Annotated[SubscriptionRequest, Body()],
    reachability_status_subscription_interface: ReachabilityStatusInterfaceDep,
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

    return await reachability_status_subscription_interface.create_subscription(
        req, device
    )
