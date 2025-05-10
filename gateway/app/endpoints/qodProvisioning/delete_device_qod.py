from fastapi import APIRouter

from app.schemas.qodProvisioning import ProvisioningInfo
from app.drivers.qodProvisioning import qodProvisioningInterfaceDep

router = APIRouter()


@router.get("/device-qos/{provisioningId}")
async def delete_qod(
    provisioningId: str,
    qodProvisioning_interface: qodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.delete_qod_provisioning(
        provisioningId
    )
    return provisioning_info
