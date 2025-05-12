from fastapi import APIRouter
from app.settings import QodProvisioningBackend, settings

match settings.qod_provisioning.qod_provisioning_backend:
    case QodProvisioningBackend.Nef:
        from .nef import router as nef_router

        router = APIRouter(prefix="/callbacks/v1")
        router.include_router(nef_router)
