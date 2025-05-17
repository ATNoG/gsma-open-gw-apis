from app.settings import settings

from .impl import NefReachabilityStatusInterface

nef_reachability_status_interface = NefReachabilityStatusInterface(
    settings.reachability_status.nef, str(settings.gateway_public_url)
)
