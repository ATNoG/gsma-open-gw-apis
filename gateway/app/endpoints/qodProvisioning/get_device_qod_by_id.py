from fastapi import APIRouter

from app.drivers.qodProvisioning.nef import NEFQoDProvisioningInterface
from app.schemas.qodProvisioning import ProvisioningInfo

router = APIRouter()


@router.get("/device-qos/{provisioningId}", response_model_exclude_unset=True)
async def get_qod_information_by_id(
    provisioningId: str, qodProvisioning_interface: NEFQoDProvisioningInterface
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.get_qod_information_by_id(
        provisioningId
    )
    return provisioning_info
