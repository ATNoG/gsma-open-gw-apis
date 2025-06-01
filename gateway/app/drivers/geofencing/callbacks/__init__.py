from fastapi import APIRouter

from app.settings import GeofencingBackend, settings


router = APIRouter(prefix="/callbacks/v1")
match settings.geofencing.backend:
    case GeofencingBackend.NEF:
        from .nef import router as nef_router

        router.include_router(nef_router)
