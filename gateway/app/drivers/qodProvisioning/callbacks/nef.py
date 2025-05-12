from app.schemas.nef_schemas.afSessionWithQos import UserPlaneNotificationData
from fastapi import APIRouter

from app.drivers.qodProvisioning.nef import nef_qod_provisioning_interface

router = APIRouter()


@router.post("/qos/{provisioning_id}")
async def receive_callback_message(
    provisioning_id: str,
    body: UserPlaneNotificationData,
) -> None:
    await nef_qod_provisioning_interface.send_callback_message(body, provisioning_id)
