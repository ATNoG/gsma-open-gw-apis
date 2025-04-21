from typing import Any, Union

from fastapi import APIRouter

from app.endpoints import geofencing_webhook
from app.schemas import ErrorInfo

from . import geofencing_subscriptions, smsotp

responses: dict[Union[int, str], dict[str, Any]] = {
    400: {
        "description": "Problem with the client request",
        "model": ErrorInfo,
    }
}

router = APIRouter(responses=responses)
router.include_router(smsotp.router)
router.include_router(geofencing_subscriptions.router)
router.include_router(geofencing_webhook.router)
