from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError

from app.drivers.qodProvisioning import QodProvisioningInterfaceDep
from app.drivers.quality_on_demand import QodInterfaceDep
from app.schemas.quality_on_demand import RetrieveSessionsInput, SessionInfo

router = APIRouter()


@router.post("/retrieve-sessions", response_model_exclude_none=True)
async def get_qod_information_by_id(
    req: RetrieveSessionsInput,
    qod_interface: QodInterfaceDep,
) -> SessionInfo:
    if req.device is None:
        raise RequestValidationError("Device must be set")

    return await qod_provisioning_interface.get_qod_information_device(req.device)
