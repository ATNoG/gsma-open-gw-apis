from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from app.exceptions import ApiException
from app.schemas import ErrorInfo


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> Response:
        body = ErrorInfo(status=400, code="INVALID_ARGUMENT", message=str(exc))
        return JSONResponse(status_code=400, content=jsonable_encoder(body))

    @app.exception_handler(ApiException)
    async def api_exception(request: Request, exc: ApiException) -> Response:
        body = ErrorInfo(
            status=exc.status,
            code=exc.code,
            message=exc.message,
        )
        return JSONResponse(status_code=400, content=jsonable_encoder(body))
