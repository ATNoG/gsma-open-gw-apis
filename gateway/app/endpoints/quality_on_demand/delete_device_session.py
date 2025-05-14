from fastapi import APIRouter

from app.drivers.quality_on_demand import QodInterfaceDep
from app.schemas.qodProvisioning import ProvisioningInfo
from app.drivers.qodProvisioning import QodProvisioningInterfaceDep

router = APIRouter()


@router.delete("/sessions/{sessionId}", response_model_exclude_none=True)
async def delete_qod(
    sessionId: str,
    qod_interface: QodInterfaceDep,
):
    await qod_interface.delete_qod_provisioning(sessionId)
