from fastapi import APIRouter

from app.endpoints import auth, trucks

router = APIRouter()
router.include_router(auth.router, tags=["Auth"])
router.include_router(trucks.router, tags=["Trucks"])
