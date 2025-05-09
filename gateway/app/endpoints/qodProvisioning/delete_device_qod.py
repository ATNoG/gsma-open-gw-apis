from fastapi import APIRouter

from app.drivers.qodProvisioning.nef import NEFQoDProvisioningInterface
from app.schemas.qodProvisioning import ProvisioningInfo

router = APIRouter()


@router.get("/device-qos/{provisioningId}", response_model_exclude_unset=True)
async def delete_qod(
    provisioningId: str, qodProvisioning_interface: NEFQoDProvisioningInterface
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.delete_qod_provisioning(
        provisioningId
    )
    return provisioning_info
