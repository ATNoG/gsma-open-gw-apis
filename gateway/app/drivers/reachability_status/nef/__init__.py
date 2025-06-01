from app.settings import ReachabilityStatusBackend, settings

from .impl import NefReachabilityStatusInterface

if settings.reachability_status.backend != ReachabilityStatusBackend.Nef:
    raise RuntimeError(
        "Reachability status NEF driver instantiated but backend isn't nef"
    )

nef_reachability_status_interface = NefReachabilityStatusInterface(
    settings.reachability_status.nef, str(settings.gateway_public_url)
)
