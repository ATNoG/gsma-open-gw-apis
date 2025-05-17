from fastapi import APIRouter
from app.settings import QodBackend, settings

router = APIRouter(prefix="/callbacks/v1")

match settings.qod.backend:
    case QodBackend.Nef:
        from .nef import router as nef_router

        router.include_router(nef_router)
