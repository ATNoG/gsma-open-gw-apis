from fastapi import APIRouter
from app.settings import QodProvisioningBackend, settings

router = APIRouter(prefix="/callbacks/v1")

match settings.qod_provisioning.backend:
    case QodProvisioningBackend.Nef:
        from .nef import router as nef_router

        router.include_router(nef_router)
