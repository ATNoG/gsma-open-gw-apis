from http import HTTPStatus
from app.schemas.nef_schemas.afSessionWithQos import UserPlaneNotificationData
from fastapi import APIRouter

from app.drivers.quality_on_demand.nef import nef_qod_interface

router = APIRouter()


@router.post("/qod/{provisioning_id}", status_code=HTTPStatus.NO_CONTENT)
async def receive_callback_message(
    provisioning_id: str,
    body: UserPlaneNotificationData,
) -> None:
    await nef_qod_interface.send_callback_message(body, provisioning_id)
