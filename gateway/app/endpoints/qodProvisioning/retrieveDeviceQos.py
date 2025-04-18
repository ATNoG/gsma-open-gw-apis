from fastapi import APIRouter

from app.drivers.qodProvisioning.provisioning import RedisQoDProvisioningInterface
from app.schemas.qodProvisioning import ProvisioningInfo, RetrieveProvisioningByDevice

router = APIRouter()


@router.get("/retrieve-device-qos")
async def get_qod_information_by_id(
    device: RetrieveProvisioningByDevice,
    qodProvisioning_interface: RedisQoDProvisioningInterface,
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.get_qod_information_device(
        device
    )
    return provisioning_info
