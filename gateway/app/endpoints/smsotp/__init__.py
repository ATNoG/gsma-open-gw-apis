from fastapi import APIRouter

from . import send

router = APIRouter(prefix="/one-time-password-sms/v1")
router.include_router(send.router)
