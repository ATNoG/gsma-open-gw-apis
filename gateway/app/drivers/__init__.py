from fastapi import APIRouter

from app.drivers.geofencing import callbacks as geofencing_callbacks
from app.drivers.qodProvisioning import callbacks as qod_provisioning_callbacks
from app.drivers.reachability_status import callbacks as reachability_status_callbacks
from app.drivers.quality_on_demand import callbacks as qod_callbacks

router = APIRouter()
router.include_router(qod_provisioning_callbacks.router)
router.include_router(qod_callbacks.router)
router.include_router(geofencing_callbacks.router)
router.include_router(reachability_status_callbacks.router)
