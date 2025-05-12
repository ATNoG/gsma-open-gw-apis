from fastapi import APIRouter

from app.schemas.qodProvisioning import ProvisioningInfo
from app.drivers.qodProvisioning.nef import QodProvisioningInterfaceDep

router = APIRouter()


@router.delete("/device-qos/{provisioningId}", response_model_exclude_none=True)
async def delete_qod(
    provisioningId: str,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    return await qod_provisioning_interface.delete_qod_provisioning(provisioningId)
