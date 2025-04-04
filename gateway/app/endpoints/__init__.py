from fastapi import APIRouter

from typing import Any, Union

from app.schemas import ErrorInfo

from . import smsotp

responses: dict[Union[int, str], dict[str, Any]] = {
    400: {
        "description": "Problem with the client request",
        "model": ErrorInfo,
    }
}

router = APIRouter(responses=responses)
router.include_router(smsotp.router)
