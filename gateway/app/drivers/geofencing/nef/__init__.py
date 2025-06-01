from app.drivers.geofencing.nef.nef import NefGeofencingSubscriptionInterface
from app.settings import GeofencingBackend, settings

if settings.geofencing.backend != GeofencingBackend.NEF:
    raise RuntimeError("Geofencing NEF driver instantiated but backend isn't nef")

nef_geofencing_subscription_interface = NefGeofencingSubscriptionInterface(
    settings.geofencing.nef, str(settings.gateway_public_url)
)
