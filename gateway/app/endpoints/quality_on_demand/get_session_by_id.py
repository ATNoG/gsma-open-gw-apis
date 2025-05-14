from fastapi import APIRouter

from app.drivers.quality_on_demand import QodInterfaceDep
from app.schemas.quality_on_demand import SessionInfo

router = APIRouter()


@router.get("/sessions/{sessionId}", response_model_exclude_none=True)
async def get_qod_information_by_id(
    sessionId: str, qod_interface: QodInterfaceDep
) -> SessionInfo:
    return await qod_interface.get_qod_information_by_id(sessionId)
