from fastapi import APIRouter


from . import (
    otp_sender,
    otp_validator,

)

router = APIRouter(prefix="/one-time-password-sms/v1.1.0-rc.1")
router.include_router(otp_sender.router)
router.include_router(otp_validator.router)