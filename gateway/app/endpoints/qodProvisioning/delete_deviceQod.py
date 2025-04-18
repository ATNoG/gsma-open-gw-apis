from fastapi import APIRouter

from app.drivers.qodProvisioning.provisioning import RedisQoDProvisioningInterface
from app.schemas.qodProvisioning import ProvisioningInfo

router = APIRouter()


@router.get("/device-qos/{provisioningId}")
async def delete_qod(
    provisioningId: str, qodProvisioning_interface: RedisQoDProvisioningInterface
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.delete_qod_provisioning(
        provisioningId
    )
    return provisioning_info
