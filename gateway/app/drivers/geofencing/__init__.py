from typing import Annotated

from fastapi import Depends

from .subscriptions import RedisGeofencingSubscriptionInterface
from app.interfaces.geofencing_subscriptions import GeofencingSubscriptionInterface

geofencing_subscription_interface: GeofencingSubscriptionInterface = (
    RedisGeofencingSubscriptionInterface()
)


def get_geofencing_subscription_interface() -> GeofencingSubscriptionInterface:
    return geofencing_subscription_interface


GeofencingSubscriptionInterfaceDep = Annotated[
    GeofencingSubscriptionInterface, Depends(get_geofencing_subscription_interface)
]
