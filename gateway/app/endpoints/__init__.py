from typing import Any, Union

from fastapi import APIRouter

from app.endpoints import geofencing_webhook
from app.schemas import ErrorInfo

from . import geofencing_subscriptions, location, qodProvisioning, qos_profiles, smsotp

responses: dict[Union[int, str], dict[str, Any]] = {
    400: {
        "description": "Problem with the client request",
        "model": ErrorInfo,
    }
}

router = APIRouter(responses=responses)
router.include_router(smsotp.router, tags=["SMS OTP"])
router.include_router(qos_profiles.router, tags=["QoS Profiles"])
router.include_router(location.router, tags=["Location"])
router.include_router(qodProvisioning.router, tags=["QoD Provisioning"])
router.include_router(
    geofencing_subscriptions.router, tags=["Geofencing Subscriptions"]
)
router.include_router(geofencing_webhook.router)
