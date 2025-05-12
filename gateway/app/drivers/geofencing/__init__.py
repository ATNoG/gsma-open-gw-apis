from typing import Annotated

from fastapi import Depends

from app.interfaces.geofencing_subscriptions import GeofencingSubscriptionInterface

from .subscriptions import RedisGeofencingSubscriptionInterface

geofencing_subscription_interface: GeofencingSubscriptionInterface = (
    RedisGeofencingSubscriptionInterface()
)


def get_geofencing_subscription_interface() -> GeofencingSubscriptionInterface:
    return geofencing_subscription_interface


GeofencingSubscriptionInterfaceDep = Annotated[
    GeofencingSubscriptionInterface, Depends(get_geofencing_subscription_interface)
]
