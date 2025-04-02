from fastapi import APIRouter

from . import smsotp

router = APIRouter()
router.include_router(smsotp.router)
