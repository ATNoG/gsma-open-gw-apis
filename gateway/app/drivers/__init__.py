from fastapi import APIRouter

from app.drivers.qodProvisioning import callbacks as qodProvisioningCallbacks

router = APIRouter()
router.include_router(qodProvisioningCallbacks.router)
