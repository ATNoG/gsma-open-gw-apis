from fastapi import APIRouter

from . import (
    create_deviceQos,
    get_deviceQod_by_id,
    delete_deviceQod,
    retrieveDeviceQos,
)

router = APIRouter(prefix="/qod-provisioning/v0.1")
router.include_router(create_deviceQos.router)
router.include_router(get_deviceQod_by_id.router)
router.include_router(delete_deviceQod.router)
router.include_router(retrieveDeviceQos.router)
