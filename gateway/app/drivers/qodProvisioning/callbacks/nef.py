from app.schemas.afSessionWithQos import UserPlaneNotificationData
from fastapi import APIRouter, status

from app.drivers.qodProvisioning import qodProvisioningInterfaceDep

router = APIRouter()


@router.post("/qos/{provisioning_id}")
async def receive_callback_message(
    provisioning_id: str,
    body: UserPlaneNotificationData,
    qodProvisioning_interface: qodProvisioningInterfaceDep,
) -> None:
    await qodProvisioning_interface.send_callback_message(body, provisioning_id)
