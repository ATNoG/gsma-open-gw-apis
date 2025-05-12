from fastapi import APIRouter

from app.schemas.qodProvisioning import ProvisioningInfo, RetrieveProvisioningByDevice
from app.drivers.qodProvisioning.nef import QodProvisioningInterfaceDep

router = APIRouter()


@router.post("/retrieve-device-qos", response_model_exclude_none=True)
async def get_qod_information_by_id(
    device: RetrieveProvisioningByDevice,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    return await qod_provisioning_interface.get_qod_information_device(device)
