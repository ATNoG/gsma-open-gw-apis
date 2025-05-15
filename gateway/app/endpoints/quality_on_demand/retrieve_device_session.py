from typing import List
from fastapi import APIRouter

from app.drivers.quality_on_demand import QodInterfaceDep
from app.exceptions import MissingDevice
from app.schemas.quality_on_demand import RetrieveSessionsInput, SessionInfo

router = APIRouter()


@router.post("/retrieve-sessions", response_model_exclude_unset=True)
async def get_qod_information_by_device(
    req: RetrieveSessionsInput,
    qod_interface: QodInterfaceDep,
) -> List[SessionInfo]:
    if req.device is None:
        raise MissingDevice()

    return await qod_interface.get_qod_information_device(req.device)
