from fastapi import APIRouter

from app.drivers.qodProvisioning.nef import NEFQoDProvisioningInterface
from app.schemas.qodProvisioning import CreateProvisioning, ProvisioningInfo

router = APIRouter()


@router.post("/device-qos", response_model_exclude_unset=True)
async def crate_provisioning(
    req: CreateProvisioning, qodProvisioning_interface: NEFQoDProvisioningInterface
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.create_provisioning(req)
    return provisioning_info
