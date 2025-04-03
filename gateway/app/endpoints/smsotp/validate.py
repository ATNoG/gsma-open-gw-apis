from fastapi import APIRouter, HTTPException, status

from app.interfaces.otp import (
    OTPExpiredCodeError,
    OTPInvalidCodeError,
    OTPNotFoundError,
    OTPTooManyAttemptsError,
)
from app.drivers.otp import OTPInterfaceDep
from app.schemas.smsotp import ValidateCodeBody

router = APIRouter()


@router.post("/validate-code", status_code=status.HTTP_204_NO_CONTENT)
async def send_code(body: ValidateCodeBody, otp_interface: OTPInterfaceDep) -> None:
    try:
        await otp_interface.verify_otp(body.authenticationId, body.code)
    except (OTPNotFoundError, OTPInvalidCodeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not valid")
    except OTPTooManyAttemptsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Too many attempts"
        )
    except OTPExpiredCodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired")
