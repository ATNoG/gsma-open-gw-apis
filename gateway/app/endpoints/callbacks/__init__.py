from fastapi import APIRouter

from . import qodProvisioning


router = APIRouter(prefix="/callbacks/v1")
router.include_router(qodProvisioning.router)
