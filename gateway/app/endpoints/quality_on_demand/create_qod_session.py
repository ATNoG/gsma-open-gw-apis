from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError

from app.drivers.quality_on_demand import QodInterfaceDep
from app.schemas.quality_on_demand import CreateSession, SessionInfo


router = APIRouter()


@router.post("/sessions", response_model_exclude_none=True)
async def create_provisioning(
    req: CreateSession,
    qod_interface: QodInterfaceDep,
) -> SessionInfo:
    if req.device is None:
        raise RequestValidationError("Device must be set")

    return await qod_interface.create_provisioning(req, req.device)
