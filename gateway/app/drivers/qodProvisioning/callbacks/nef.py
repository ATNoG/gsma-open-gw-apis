from app.schemas.afSessionWithQos import UserPlaneNotificationData
from fastapi import APIRouter

from app.drivers.qodProvisioning import QodProvisioningInterfaceDep

router = APIRouter()


@router.post("/qos/{provisioning_id}")
async def receive_callback_message(
    provisioning_id: str,
    body: UserPlaneNotificationData,
    qod_provisioning_interface: QodProvisioningInterfaceDep,
) -> None:
    await qod_provisioning_interface.send_callback_message(body, provisioning_id)
