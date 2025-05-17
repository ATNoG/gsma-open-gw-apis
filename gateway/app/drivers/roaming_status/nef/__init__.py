from app.settings import settings

from .impl import NefRoamingStatusInterface

nef_roaming_status_interface = NefRoamingStatusInterface(
    settings.reachability_status.nef
)
