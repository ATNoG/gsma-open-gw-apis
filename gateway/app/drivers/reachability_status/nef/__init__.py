from app.settings import settings
from app.drivers.nef_auth import NEFAuth

from .impl import NefReachabilityStatusInterface

nef_url = str(settings.nef_url).rstrip("/")
nef_auth = NEFAuth(settings.nef_url, settings.nef_username, settings.nef_password)
nef_reachability_status_interface = NefReachabilityStatusInterface(
    f"{nef_url}/{settings.reachability_status.nef_base_path.strip('/')}",
    settings.reachability_status.af_id,
    nef_auth,
    str(settings.gateway_url).rstrip("/"),
)
