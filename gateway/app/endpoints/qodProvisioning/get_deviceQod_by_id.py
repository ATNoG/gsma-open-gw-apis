from fastapi import APIRouter

from app.drivers.qodProvisioning.provisioning import RedisQoDProvisioningInterface
from app.schemas.qodProvisioning import ProvisioningInfo

router = APIRouter()


@router.get("/device-qos/{provisioningId}")
async def get_qod_information_by_id(
    provisioningId: str, qodProvisioning_interface: RedisQoDProvisioningInterface
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.get_qod_information_by_id(
        provisioningId
    )
    return provisioning_info
