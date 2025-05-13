from typing import Annotated

from fastapi import Depends

from app.interfaces.geofencing_subscriptions import GeofencingSubscriptionInterface
from app.settings import GeofencingBackend, settings

geofencing_subscription_interface: GeofencingSubscriptionInterface
match settings.geofencing.backend:
    case GeofencingBackend.NEF:
        from .nef import nef_geofencing_subscription_interface

        geofencing_subscription_interface = nef_geofencing_subscription_interface


def get_geofencing_subscription_interface() -> GeofencingSubscriptionInterface:
    return geofencing_subscription_interface


GeofencingSubscriptionInterfaceDep = Annotated[
    GeofencingSubscriptionInterface, Depends(get_geofencing_subscription_interface)
]
