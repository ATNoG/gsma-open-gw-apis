from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError

from app.schemas.qodProvisioning import ProvisioningInfo, RetrieveProvisioningByDevice
from app.drivers.qodProvisioning import QodProvisioningInterfaceDep

router = APIRouter()


@router.post("/retrieve-device-qos", response_model_exclude_none=True)
async def get_qod_information_by_id(
    req: RetrieveProvisioningByDevice,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    if req.device is None:
        raise RequestValidationError("Device must be set")

    return await qod_provisioning_interface.get_qod_information_device(req.device)
