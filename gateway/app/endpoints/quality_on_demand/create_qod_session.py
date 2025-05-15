from http import HTTPStatus
from fastapi import APIRouter

from app.drivers.quality_on_demand import QodInterfaceDep
from app.exceptions import MissingDevice
from app.schemas.quality_on_demand import CreateSession, SessionInfo


router = APIRouter()


@router.post(
    "/sessions", response_model_exclude_unset=True, status_code=HTTPStatus.CREATED
)
async def create_session(
    req: CreateSession,
    qod_interface: QodInterfaceDep,
) -> SessionInfo:
    if req.device is None:
        raise MissingDevice()

    return await qod_interface.create_provisioning(req, req.device)
