from typing import Annotated

from fastapi import Depends

from app.drivers.nef_auth import NEFAuth
from app.interfaces.geofencing_subscriptions import GeofencingSubscriptionInterface
from app.settings import settings

from .subscriptions import RedisGeofencingSubscriptionInterface

nef_auth = NEFAuth(settings.nef_url, settings.nef_username, settings.nef_password)
geofencing_subscription_interface: GeofencingSubscriptionInterface = (
    RedisGeofencingSubscriptionInterface(settings.nef_url, nef_auth)
)


def get_geofencing_subscription_interface() -> GeofencingSubscriptionInterface:
    return geofencing_subscription_interface


GeofencingSubscriptionInterfaceDep = Annotated[
    GeofencingSubscriptionInterface, Depends(get_geofencing_subscription_interface)
]
