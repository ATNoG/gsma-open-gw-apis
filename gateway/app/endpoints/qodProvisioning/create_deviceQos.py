from fastapi import APIRouter

from app.drivers.qodProvisioning.provisioning import QoDProvisioningInterface
from app.schemas.qodProvisioning import CreateProvisioning, ProvisioningInfo

router = APIRouter()


@router.post("/device-qos")
async def crate_provisioning(
    req: CreateProvisioning, qodProvisioning_interface: QoDProvisioningInterface
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.crate_provisioning(req)
    return provisioning_info
