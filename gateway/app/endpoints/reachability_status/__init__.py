from fastapi import APIRouter

from app.exceptions import MissingDevice
from app.drivers.reachability_status import ReachabilityStatusInterfaceDep
from app.schemas.reachability_status import (
    ReachabilityStatusResponse,
    RequestReachabilityStatus,
)

router = APIRouter(prefix="/device-reachability-status/v1")


@router.post(
    "/retrieve", response_model_exclude_unset=True, response_model_exclude_none=True
)
async def retrieve_reachability_status(
    body: RequestReachabilityStatus,
    reachability_status_interface: ReachabilityStatusInterfaceDep,
) -> ReachabilityStatusResponse:
    if body.device is None:
        raise MissingDevice()

    return await reachability_status_interface.get_reachability_status(body.device)
