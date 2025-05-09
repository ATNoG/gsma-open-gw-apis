from fastapi import APIRouter

from . import (
    create_device_qos,
    delete_device_qod,
    get_device_qod_by_id,
    retrieve_device_qos,
)


router = APIRouter(prefix="/qod-provisioning/v0.1")
router.include_router(create_device_qos.router)
router.include_router(get_device_qod_by_id.router)
router.include_router(delete_device_qod.router)
router.include_router(retrieve_device_qos.router)
