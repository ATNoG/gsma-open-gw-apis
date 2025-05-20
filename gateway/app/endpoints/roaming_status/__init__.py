from fastapi import APIRouter

from app.exceptions import MissingDevice
from app.schemas.roaming_status import RoamingStatusRequest, RoamingStatusResponse
from app.drivers.roaming_status import RoamingStatusInterfaceDep
from app.utils.mcc_to_country_code import get_country_names

from .subscriptions import router as sub_router_internal

router = APIRouter(prefix="/device-roaming-status/v1")
subscriptions_router = sub_router_internal


@router.post(
    "/retrieve", response_model_exclude_unset=True, response_model_exclude_none=True
)
async def retrieve_roaming_status(
    body: RoamingStatusRequest,
    roaming_status_interface: RoamingStatusInterfaceDep,
) -> RoamingStatusResponse:
    if body.device is None:
        raise MissingDevice()

    res = await roaming_status_interface.get_roaming_status(body.device)

    if res.countryCode is not None and res.countryName is None:
        res.countryName = get_country_names(res.countryCode)

    return res
