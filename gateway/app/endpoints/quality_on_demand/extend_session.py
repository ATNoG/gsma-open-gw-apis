from fastapi import APIRouter

from app.drivers.quality_on_demand import QodInterfaceDep
from app.schemas.quality_on_demand import ExtendSessionDuration, SessionInfo

router = APIRouter()


@router.post("/sessions/{sessionId}/extend", response_model_exclude_none=True)
async def extend_session_duration(
    sessionId: str, req: ExtendSessionDuration, qod_interface: QodInterfaceDep
) -> SessionInfo:
    return await qod_interface.extend_session(sessionId, req)
