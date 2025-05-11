from fastapi import APIRouter

from app.schemas.qodProvisioning import TriggerProvisioning, ProvisioningInfo
from app.drivers.qodProvisioning import QodProvisioningInterfaceDep

router = APIRouter()


@router.post("/device-qos")
async def crate_provisioning(
    req: TriggerProvisioning,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    return await qod_provisioning_interface.create_provisioning(req)
