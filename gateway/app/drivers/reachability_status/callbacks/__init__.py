from fastapi import APIRouter

from app.settings import ReachabilityStatusBackend, settings

from .nef import router as nef_router


router: APIRouter = APIRouter(prefix="/callbacks/v1")
match settings.reachability_status.backend:
    case ReachabilityStatusBackend.Nef:
        router.include_router(nef_router)
