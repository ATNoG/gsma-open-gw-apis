from fastapi import APIRouter

from app.drivers.qodProvisioning import callbacks

router = APIRouter()
router.include_router(callbacks.router)
