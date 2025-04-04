from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError

from app.schemas import ErrorInfo
from app.interfaces.otp import (
    OTPExpiredCodeError,
    OTPInvalidCodeError,
    OTPNotFoundError,
    OTPTooManyAttemptsError,
)


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> Response:
        body = ErrorInfo(status=400, code="INVALID_ARGUMENT", message=str(exc))
        return JSONResponse(status_code=400, content=jsonable_encoder(body))

    @app.exception_handler(OTPNotFoundError)
    @app.exception_handler(OTPInvalidCodeError)
    async def otp_invalid_exception_handler(
        request: Request, exc: Exception
    ) -> Response:
        body = ErrorInfo(
            status=400,
            code="ONE_TIME_PASSWORD_SMS.INVALID_OTP",
            message="The provided OTP is not valid for this authenticationId",
        )
        return JSONResponse(status_code=400, content=jsonable_encoder(body))

    @app.exception_handler(OTPTooManyAttemptsError)
    async def otp_too_many_attempts_exception_handler(
        request: Request, exc: Exception
    ) -> Response:
        body = ErrorInfo(
            status=400,
            code="ONE_TIME_PASSWORD_SMS.VERIFICATION_FAILED",
            message="The maximum number of attempts for this authenticationId was exceeded without providing a valid OTP",
        )
        return JSONResponse(status_code=400, content=jsonable_encoder(body))

    @app.exception_handler(OTPExpiredCodeError)
    async def otp_expired_exception_handler(
        request: Request, exc: Exception
    ) -> Response:
        body = ErrorInfo(
            status=400,
            code="ONE_TIME_PASSWORD_SMS.VERIFICATION_EXPIRED",
            message="The authenticationId is no longer valid",
        )
        return JSONResponse(status_code=400, content=jsonable_encoder(body))
