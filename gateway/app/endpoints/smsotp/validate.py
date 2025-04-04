from fastapi import APIRouter, status

from typing import Any, Union

from app.drivers.otp import OTPInterfaceDep
from app.schemas import ErrorInfo
from app.schemas.smsotp import ValidateCodeBody


router = APIRouter()

responses: dict[Union[int, str], dict[str, Any]] = {
    400: {
        "description": """\
Problem with the client request. In addition to regular scenario of `INVALID_ARGUMENT`, another scenarios may exist:
  - Too many unsuccessful attempts (`{"code": "ONE_TIME_PASSWORD_SMS.VERIFICATION_FAILED","message": "The maximum number of attempts for this authenticationId was exceeded without providing a valid OTP"}`)
  - Expired authenticationId (`{"code": "ONE_TIME_PASSWORD_SMS.VERIFICATION_EXPIRED","message": "The authenticationId is no longer valid"}`)
  - OTP is not valid for the provided authenticationId (`{"code": "ONE_TIME_PASSWORD_SMS.INVALID_OTP","message": "The provided OTP is not valid for this authenticationId"}`)
        """,
        "model": ErrorInfo,
    }
}


@router.post(
    "/validate-code", status_code=status.HTTP_204_NO_CONTENT, responses=responses
)
async def send_code(body: ValidateCodeBody, otp_interface: OTPInterfaceDep) -> None:
    await otp_interface.verify_otp(body.authenticationId, body.code)
