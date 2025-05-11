from app.interfaces.qodProvisioning import ProvisioningConflict
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
from app.interfaces.qos_profiles import QoSProfileNotFound


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

    @app.exception_handler(QoSProfileNotFound)
    async def qos_profile_not_found_exception_handler(
        request: Request, exc: QoSProfileNotFound
    ) -> Response:
        body = ErrorInfo(
            status=404,
            code="NOT_FOUND",
            message="The QoS profile could not be found",
        )
        return JSONResponse(status_code=404, content=jsonable_encoder(body))

    @app.exception_handler(ProvisioningConflict)
    async def provisioning_conflict_exception_error(
        request: Request, exc: QoSProfileNotFound
    ) -> Response:
        body = ErrorInfo(
            status=409,
            code="CONFLICT",
            message="There is another existing provisioning for the same device",
        )
        return JSONResponse(status_code=409, content=jsonable_encoder(body))
