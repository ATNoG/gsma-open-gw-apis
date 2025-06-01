from app.settings import RoamingStatusBackend, settings

from .impl import NefRoamingStatusInterface

if settings.roaming_status.backend != RoamingStatusBackend.Nef:
    raise RuntimeError("Roaming status NEF driver instantiated but backend isn't nef")

nef_roaming_status_interface = NefRoamingStatusInterface(
    settings.roaming_status.nef, str(settings.gateway_public_url)
)
