from fastapi import APIRouter

from app.schemas.qodProvisioning import TriggerProvisioning, ProvisioningInfo
from app.drivers.qodProvisioning.nef import QodProvisioningInterfaceDep

router = APIRouter()


@router.post("/device-qos", response_model_exclude_none=True)
async def create_provisioning(
    req: TriggerProvisioning,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    return await qod_provisioning_interface.create_provisioning(req)
