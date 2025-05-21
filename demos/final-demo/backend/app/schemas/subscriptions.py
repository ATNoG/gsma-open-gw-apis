from enum import Enum
from typing import Union

from pydantic import BaseModel


class ReachabilityEventType(str, Enum):
    v0_reachability_data = "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-data"
    v0_reachability_sms = (
        "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-sms"
    )
    v0_reachability_disconnected = "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-disconnected"


class GeofencingEventType(str, Enum):
    v0_area_entered = "org.camaraproject.geofencing-subscriptions.v0.area-entered"
    v0_area_left = "org.camaraproject.geofencing-subscriptions.v0.area-left"


class CloudEvent(BaseModel):
    type: Union[ReachabilityEventType, GeofencingEventType, str]
