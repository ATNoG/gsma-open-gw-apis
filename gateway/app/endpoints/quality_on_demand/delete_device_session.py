from http import HTTPStatus
from fastapi import APIRouter

from app.drivers.quality_on_demand import QodInterfaceDep

router = APIRouter()


@router.delete("/sessions/{sessionId}", status_code=HTTPStatus.NO_CONTENT)
async def delete_qod(
    sessionId: str,
    qod_interface: QodInterfaceDep,
) -> None:
    await qod_interface.delete_qod_session(sessionId)
