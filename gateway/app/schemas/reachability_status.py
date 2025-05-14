from enum import Enum
from datetime import datetime
from typing import Annotated, Optional, List, Union

from pydantic import Field, BaseModel, TypeAdapter

from .device import Device
import app.schemas.subscriptions as subscriptions

LastStatusTime = Annotated[
    datetime,
    Field(
        description="Last time that the associated device reachability status was updated",
        examples=["2024-02-20T10:41:38.657Z"],
    ),
]


class ConnectivityType(Enum):
    DATA = "DATA"
    SMS = "SMS"


class ReachabilityStatusResponse(BaseModel):
    lastStatusTime: Optional[LastStatusTime] = None
    reachable: Annotated[
        bool, Field(description="Indicates overall device reachability")
    ]
    connectivity: Optional[List[ConnectivityType]] = None


class RequestReachabilityStatus(BaseModel):
    device: Optional[Device] = None


class CreateSubscriptionDetail(BaseModel):
    device: Optional[Device] = None


class SubscriptionConfig(BaseModel):
    subscriptionDetail: CreateSubscriptionDetail
    subscriptionExpireTime: Annotated[
        Optional[datetime],
        Field(
            description="The subscription expiration time (in date-time format) requested by the API consumer. Up to API project decision to keep it.",
            examples=["2023-01-17T13:18:23.682Z"],
        ),
    ] = None
    subscriptionMaxEvents: Annotated[
        Optional[int],
        Field(
            ge=1,
            description="Identifies the maximum number of event reports to be generated (>=1) requested by the API consumer - Once this number is reached, the subscription ends. Up to API project decision to keep it.",
            examples=[5],
        ),
    ] = None
    initialEvent: Annotated[
        Optional[bool],
        Field(
            description="Set to `true` by API consumer if consumer wants to get an event as soon as the subscription is created and current situation reflects event request.Up to API project decision to keep it.\nExample: Consumer subscribes to reachability SMS. If consumer sets initialEvent to true and device is already reachable by SMS, an event is triggered.",
        ),
    ] = None


class SubscriptionEventType(str, Enum):
    v0_reachability_data = "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-data"
    v0_reachability_sms = (
        "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-sms"
    )
    v0_reachability_disconnected = "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-disconnected"


class NotificationEventType(str, Enum):
    v0_reachability_data = "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-data"
    v0_reachability_sms = (
        "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-sms"
    )
    v0_reachability_disconnected = "org.camaraproject.device-reachability-status-subscriptions.v0.reachability-disconnected"
    v0_subscription_ends = "org.camaraproject.device-reachability-status-subscriptions.v0.subscription-ends"


class ReachabilityDataSmsDisconnected(BaseModel):
    device: Optional[Device] = None
    subscriptionId: subscriptions.SubscriptionId


class SubscriptionEnds(BaseModel):
    device: Optional[Device] = None
    terminationReason: subscriptions.TerminationReason
    subscriptionId: subscriptions.SubscriptionId
    terminationDescription: Optional[str] = None


CloudEvent = subscriptions.CloudEvent[
    NotificationEventType, Union[ReachabilityDataSmsDisconnected, SubscriptionEnds]
]
Subscription = subscriptions.Subscription[SubscriptionEventType, SubscriptionConfig]
SubscriptionTypeAdapter: TypeAdapter[Subscription] = TypeAdapter(Subscription)
SubscriptionRequest = subscriptions.SubscriptionRequest[
    SubscriptionEventType, SubscriptionConfig
]
