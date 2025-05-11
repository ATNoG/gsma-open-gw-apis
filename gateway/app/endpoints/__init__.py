from fastapi import APIRouter

from typing import Any, Union

from app.schemas import ErrorInfo

from . import smsotp, qos_profiles, location, qodProvisioning

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
router.include_router(smsotp.router)
router.include_router(qodProvisioning.router, tags=["QoD Provisioning"])
