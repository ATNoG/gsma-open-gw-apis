from app.settings import settings

from .impl import NefRoamingStatusInterface

nef_roaming_status_interface = NefRoamingStatusInterface(
    settings.roaming_status.nef
)
