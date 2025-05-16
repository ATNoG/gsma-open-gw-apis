from fastapi import APIRouter

from app.schemas.qodProvisioning import ProvisioningInfo
from app.drivers.qodProvisioning import QodProvisioningInterfaceDep

router = APIRouter()


@router.get("/device-qos/{provisioningId}", response_model_exclude_unset=True)
async def get_qod_information_by_id(
    provisioningId: str, qod_provisioning_interface: QodProvisioningInterfaceDep
) -> ProvisioningInfo:
    return await qod_provisioning_interface.get_qod_information_by_id(provisioningId)
