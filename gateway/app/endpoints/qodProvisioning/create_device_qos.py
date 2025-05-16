from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError

from app.schemas.qodProvisioning import TriggerProvisioning, ProvisioningInfo
from app.drivers.qodProvisioning import QodProvisioningInterfaceDep

router = APIRouter()


@router.post("/device-qos", response_model_exclude_unset=True)
async def create_provisioning(
    req: TriggerProvisioning,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    if req.device is None:
        raise RequestValidationError("Device must be set")

    return await qod_provisioning_interface.create_provisioning(req, req.device)
