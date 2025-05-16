from http import HTTPStatus
from fastapi import APIRouter

from app.drivers.qodProvisioning import QodProvisioningInterfaceDep

router = APIRouter()


@router.delete("/device-qos/{provisioningId}", status_code=HTTPStatus.NO_CONTENT)
async def delete_qod(
    provisioningId: str,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> None:
    await qod_provisioning_interface.delete_qod_provisioning(provisioningId)
