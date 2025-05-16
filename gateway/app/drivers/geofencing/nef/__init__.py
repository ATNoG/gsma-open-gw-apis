from app.drivers.geofencing.nef.nef import NefGeofencingSubscriptionInterface
from app.settings import settings

nef_geofencing_subscription_interface = NefGeofencingSubscriptionInterface(
    settings.geofencing.nef, str(settings.gateway_public_url)
)
