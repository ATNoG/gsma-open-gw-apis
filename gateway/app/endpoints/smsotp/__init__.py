from fastapi import APIRouter

from . import send, validate

router = APIRouter(prefix="/one-time-password-sms/v1")
router.include_router(send.router)
router.include_router(validate.router)
