from enum import Enum
from typing import Annotated, Optional, List, Union

from pydantic import Field, BaseModel, TypeAdapter

from app.schemas.device import Device
from app.schemas.common import LastStatusTime
import app.schemas.subscriptions as subscriptions


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


CloudEventData = Union[ReachabilityDataSmsDisconnected, SubscriptionEnds]
CloudEvent = subscriptions.CloudEvent[NotificationEventType, CloudEventData]
Subscription = subscriptions.Subscription[
    SubscriptionEventType, CreateSubscriptionDetail
]
SubscriptionTypeAdapter: TypeAdapter[Subscription] = TypeAdapter(Subscription)
SubscriptionRequest = subscriptions.SubscriptionRequest[
    SubscriptionEventType, CreateSubscriptionDetail
]
