from http import HTTPStatus
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app import SMSOTPAPP
from app.exceptions import ApiException


app = FastAPI()
app.include_router(SMSOTPAPP.router)


@app.exception_handler(ApiException)
def generic_exception(_req, e: ApiException):
    return JSONResponse(
        status_code=e.status,
        content={
            "status": e.status,
            "code": e.code,
            "message": e.message,
        },
    )


@app.exception_handler(Exception)
def unknown_exception(_req, _e):
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "status": HTTPStatus.INTERNAL_SERVER_ERROR,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unknown error has occured.",
        },
    )