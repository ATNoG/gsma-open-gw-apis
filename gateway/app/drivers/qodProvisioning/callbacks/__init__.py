from app.settings import QodProvisioningBackend, settings
from fastapi import APIRouter

match settings.qod_provisioning.qod_provisioning_backend:
    case QodProvisioningBackend.Nef:
        from . import nef

        router = APIRouter(prefix="/callbacks/v1")
        router.include_router(nef.router)
