from fastapi import APIRouter

from app.schemas.qodProvisioning import ProvisioningInfo
from app.drivers.qodProvisioning import qodProvisioningInterfaceDep

router = APIRouter()


@router.get("/device-qos/{provisioningId}")
async def get_qod_information_by_id(
    provisioningId: str, qodProvisioning_interface: qodProvisioningInterfaceDep
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.get_qod_information_by_id(
        provisioningId
    )
    return provisioning_info
