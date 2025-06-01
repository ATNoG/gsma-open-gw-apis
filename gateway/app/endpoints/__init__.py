from typing import Any, Union

from fastapi import APIRouter

from app.schemas import ErrorInfo
from app.settings import (
    GeofencingBackend,
    LocationBackend,
    QoSProfilesBackend,
    QodBackend,
    QodProvisioningBackend,
    ReachabilityStatusBackend,
    RoamingStatusBackend,
    SMSBackend,
    settings,
)

from . import (
    geofencing_subscriptions,
    location,
    quality_on_demand,
    qodProvisioning,
    qos_profiles,
    smsotp,
    reachability_status,
    roaming_status,
)

responses: dict[Union[int, str], dict[str, Any]] = {
    400: {
        "description": "Problem with the client request",
        "model": ErrorInfo,
    }
}

router = APIRouter(responses=responses)

if settings.sms_otp.sms_backend != SMSBackend.Disabled:
    router.include_router(smsotp.router, tags=["SMS OTP"])

if settings.qos_profiles.backend != QoSProfilesBackend.Disabled:
    router.include_router(qos_profiles.router, tags=["QoS Profiles"])

if settings.location.backend != LocationBackend.Disabled:
    router.include_router(location.router, tags=["Location"])

if settings.qod_provisioning.backend != QodProvisioningBackend.Disabled:
    router.include_router(qodProvisioning.router, tags=["QoD Provisioning"])

if settings.qod.backend != QodBackend.Disabled:
    router.include_router(quality_on_demand.router, tags=["Quality On Demand"])

if settings.geofencing.backend != GeofencingBackend.Disabled:
    router.include_router(
        geofencing_subscriptions.router, tags=["Geofencing Subscriptions"]
    )

if settings.reachability_status.backend != ReachabilityStatusBackend.Disabled:
    router.include_router(
        reachability_status.router, tags=["Device Reachability Status"]
    )
    router.include_router(
        reachability_status.subscriptions_router, tags=["Device Reachability Status"]
    )

if settings.roaming_status.backend != RoamingStatusBackend.Disabled:
    router.include_router(roaming_status.router, tags=["Device Roaming Status"])
    router.include_router(
        roaming_status.subscriptions_router, tags=["Device Roaming Status"]
    )
