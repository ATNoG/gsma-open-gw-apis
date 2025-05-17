from fastapi import APIRouter

from app.endpoints.quality_on_demand import (
    create_qod_session,
    delete_device_session,
    extend_session,
    get_session_by_id,
    retrieve_device_session,
)


router = APIRouter(prefix="/quality-on-demand/v1")
router.include_router(create_qod_session.router)
router.include_router(get_session_by_id.router)
router.include_router(delete_device_session.router)
router.include_router(extend_session.router)
router.include_router(retrieve_device_session.router)
