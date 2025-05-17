from typing import Any, Union

from app.endpoints import quality_on_demand
from fastapi import APIRouter

from app.schemas import ErrorInfo

from . import (
    geofencing_subscriptions,
    location,
    qodProvisioning,
    qos_profiles,
    smsotp,
    reachability_status,
)

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
router.include_router(quality_on_demand.router, tags=["Quality On Demand"])
router.include_router(
    geofencing_subscriptions.router, tags=["Geofencing Subscriptions"]
)
router.include_router(reachability_status.router, tags=["Device Reachability Status"])
router.include_router(
    reachability_status.subscriptions_router, tags=["Device Reachability Status"]
)
