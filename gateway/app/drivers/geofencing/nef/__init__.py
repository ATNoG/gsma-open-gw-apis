from app.drivers.geofencing.nef.nef import NefGeofencingSubscriptionInterface
from app.drivers.nef_auth import NEFAuth
from app.settings import settings

_nef_auth = NEFAuth(settings.nef_url, settings.nef_username, settings.nef_password)
nef_geofencing_subscription_interface = NefGeofencingSubscriptionInterface(
    settings.nef_url, _nef_auth
)
