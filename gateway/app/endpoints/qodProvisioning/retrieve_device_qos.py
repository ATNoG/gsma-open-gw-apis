from fastapi import APIRouter

from app.drivers.qodProvisioning.nef import NEFQoDProvisioningInterface
from app.schemas.qodProvisioning import ProvisioningInfo, RetrieveProvisioningByDevice

router = APIRouter()


@router.get("/retrieve-device-qos", response_model_exclude_unset=True)
async def get_qod_information_by_id(
    device: RetrieveProvisioningByDevice,
    qodProvisioning_interface: NEFQoDProvisioningInterface,
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.get_qod_information_device(
        device
    )
    return provisioning_info
