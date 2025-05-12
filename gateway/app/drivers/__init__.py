from fastapi import APIRouter

from app.drivers.geofencing import callbacks as geofencing_callbacks
from app.drivers.qodProvisioning import callbacks as qodProvisioningCallbacks

router = APIRouter()
router.include_router(qodProvisioningCallbacks.router)
router.include_router(geofencing_callbacks.router)
