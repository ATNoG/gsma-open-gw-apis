from fastapi import APIRouter

from app.drivers.quality_on_demand import QodInterfaceDep

router = APIRouter()


@router.delete("/sessions/{sessionId}", response_model_exclude_none=True)
async def delete_qod(
    sessionId: str,
    qod_interface: QodInterfaceDep,
) -> None:
    await qod_interface.delete_qod_session(sessionId)
