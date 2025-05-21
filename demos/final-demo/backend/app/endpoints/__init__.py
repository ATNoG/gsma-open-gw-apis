from fastapi import APIRouter

from app.endpoints import auth, notifications, trucks

router = APIRouter()
router.include_router(auth.router, tags=["Auth"])
router.include_router(trucks.router, tags=["Trucks"])

router.include_router(notifications.router)
