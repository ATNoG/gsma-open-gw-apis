from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, TypeAdapter

from app.schemas.device import Device
from app.schemas.common import Point
import app.schemas.subscriptions as subscriptions


class SubscriptionEventType(str, Enum):
    v0_area_entered = "org.camaraproject.geofencing-subscriptions.v0.area-entered"
    v0_area_left = "org.camaraproject.geofencing-subscriptions.v0.area-left"


class NotificationEventType(str, Enum):
    v0_area_entered = "org.camaraproject.geofencing-subscriptions.v0.area-entered"
    v0_area_left = "org.camaraproject.geofencing-subscriptions.v0.area-left"
    v0_subscription_ends = (
        "org.camaraproject.geofencing-subscriptions.v0.subscription-ends"
    )


class AreaType(str, Enum):
    CIRCLE = "CIRCLE"


class Area(BaseModel):
    areaType: AreaType


class Circle(Area):
    areaType: Literal[AreaType.CIRCLE] = AreaType.CIRCLE
    center: Point
    radius: Annotated[
        int,
        Field(
            ge=1,
            le=200000,
            description="Expected accuracy for the subscription event of device location, in meters from `center`.\nNote: The area surface could be restricted locally depending on regulations. Implementations may enforce a larger minimum radius (e.g. 1000 meters).\n",
        ),
    ]


class AreaLeft(BaseModel):
    device: Optional[Device] = None
    area: Area
    subscriptionId: subscriptions.SubscriptionId


class AreaEntered(BaseModel):
    device: Optional[Device] = None
    area: Circle
    subscriptionId: subscriptions.SubscriptionId


class SubscriptionEnds(BaseModel):
    device: Optional[Device] = None
    area: Circle
    terminationReason: subscriptions.TerminationReason
    terminationDescription: Annotated[
        Optional[str],
        Field(description="Explanation why a subscription ended or had to end."),
    ] = None
    subscriptionId: subscriptions.SubscriptionId


class SubscriptionDetail(BaseModel):
    device: Optional[Device] = None
    area: Circle


CloudEventData = Union[AreaEntered, AreaLeft, SubscriptionEnds]
CloudEvent = subscriptions.CloudEvent[NotificationEventType, CloudEventData]
Subscription = subscriptions.Subscription[SubscriptionEventType, SubscriptionDetail]
SubscriptionTypeAdapter: TypeAdapter[Subscription] = TypeAdapter(Subscription)
SubscriptionRequest = subscriptions.SubscriptionRequest[
    SubscriptionEventType, SubscriptionDetail
]
