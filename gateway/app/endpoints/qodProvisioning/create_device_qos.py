from fastapi import APIRouter

from app.schemas.qodProvisioning import CreateProvisioning, ProvisioningInfo
from app.drivers.qodProvisioning import qodProvisioningInterfaceDep

router = APIRouter()


@router.post("/device-qos")
async def crate_provisioning(
    req: CreateProvisioning,
    qodProvisioning_interface: qodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.create_provisioning(req)
    return provisioning_info
