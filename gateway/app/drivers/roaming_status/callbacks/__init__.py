from fastapi import APIRouter

from app.settings import RoamingStatusBackend, settings

router: APIRouter = APIRouter(prefix="/callbacks/v1")
match settings.roaming_status.backend:
    case RoamingStatusBackend.Nef:
        from .nef import router as nef_router

        router.include_router(nef_router)
