from fastapi import APIRouter

from app.schemas.qodProvisioning import ProvisioningInfo, RetrieveProvisioningByDevice
from app.drivers.qodProvisioning import qodProvisioningInterfaceDep

router = APIRouter()


@router.get("/retrieve-device-qos")
async def get_qod_information_by_id(
    device: RetrieveProvisioningByDevice,
    qodProvisioning_interface: qodProvisioningInterfaceDep,
) -> ProvisioningInfo:
    provisioning_info = await qodProvisioning_interface.get_qod_information_device(
        device
    )
    return provisioning_info
