from fastapi import APIRouter

from app.schemas.qodProvisioning import ProvisioningInfo
from app.drivers.qodProvisioning import QodProvisioningInterfaceDep

router = APIRouter()


@router.delete("/device-qos/{provisioningId}")
async def delete_qod(
    provisioningId: str,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    return await qod_provisioning_interface.delete_qod_provisioning(provisioningId)
