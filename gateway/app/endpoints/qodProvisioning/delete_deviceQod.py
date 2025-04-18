from fastapi import APIRouter

from app.drivers.qodProvisioning.provisioning import QoDProvisioningInterface
from app.schemas.qodProvisioning import ProvisioningInfo

router = APIRouter()


@router.get("/device-qos/{provisioningId}")
async def delete_qod(
    provisioningId: str, qodProvisioning_interface: QoDProvisioningInterface
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.delete_qod_provisioning(
        provisioningId
    )
    return provisioning_info
