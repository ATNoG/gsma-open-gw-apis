from fastapi import APIRouter

from app.settings import ReachabilityStatusBackend, settings

router: APIRouter = APIRouter(prefix="/callbacks/v1")
match settings.reachability_status.backend:
    case ReachabilityStatusBackend.Nef:
        from .nef import router as nef_router

        router.include_router(nef_router)
