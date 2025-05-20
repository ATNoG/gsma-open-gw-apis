from enum import Enum
from typing import Optional, Annotated, List, Union

from pydantic import BaseModel, Field, TypeAdapter

from app.schemas.device import Device
from app.schemas.common import LastStatusTime
import app.schemas.subscriptions as subscriptions
from app.schemas.subscriptions import SubscriptionId, TerminationReason

ActiveRoaming = Annotated[
    bool, Field(description="Roaming status. True, if it is roaming")
]

CountryCode = Annotated[
    int,
    Field(
        description="The Mobile country code (MCC) as an geographic region identifier for the country and the dependent areas.",
    ),
]
CountryName = Annotated[
    List[str],
    Field(
        description="The ISO 3166 ALPHA-2 country-codes of mapped to mobile country code(MCC). If there is mapping of one MCC to multiple countries, then we have list of countries. If there is no mapping of MCC to any country, then an empty array [] shall be returned..",
    ),
]


class RoamingStatusResponse(BaseModel):
    lastStatusTime: Optional[LastStatusTime] = None
    roaming: ActiveRoaming
    countryCode: Optional[CountryCode] = None
    countryName: Optional[CountryName] = None


class RoamingStatusRequest(BaseModel):
    device: Optional[Device] = None


class NotificationEventType(str, Enum):
    v0_roaming_status = (
        "org.camaraproject.device-roaming-status-subscriptions.v0.roaming-status"
    )
    v0_roaming_on = (
        "org.camaraproject.device-roaming-status-subscriptions.v0.roaming-on"
    )
    v0_roaming_off = (
        "org.camaraproject.device-roaming-status-subscriptions.v0.roaming-off"
    )
    v0_roaming_change_country = "org.camaraproject.device-roaming-status-subscriptions.v0.roaming-change-country"
    v0_subscription_ends = (
        "org.camaraproject.device-roaming-status-subscriptions.v0.subscription-ends"
    )


class SubscriptionEventType(str, Enum):
    v0_roaming_status = (
        "org.camaraproject.device-roaming-status-subscriptions.v0.roaming-status"
    )
    v0_roaming_on = (
        "org.camaraproject.device-roaming-status-subscriptions.v0.roaming-on"
    )
    v0_roaming_off = (
        "org.camaraproject.device-roaming-status-subscriptions.v0.roaming-off"
    )
    v0_roaming_change_country = "org.camaraproject.device-roaming-status-subscriptions.v0.roaming-change-country"


class BasicDeviceEventData(BaseModel):
    device: Optional[Device] = None
    subscriptionId: SubscriptionId


class RoamingStatus(BasicDeviceEventData):
    roaming: bool = Field(..., description="Roaming status. True, if it is roaming.")
    countryCode: Optional[CountryCode] = None
    countryName: Optional[CountryName] = None


class RoamingChangeCountry(BasicDeviceEventData):
    countryCode: CountryCode
    countryName: CountryName


class SubscriptionEnds(BasicDeviceEventData):
    terminationReason: TerminationReason
    terminationDescription: Optional[str] = None


class CreateSubscriptionDetail(BaseModel):
    device: Optional[Device] = None


CloudEventData = Union[
    BasicDeviceEventData, RoamingStatus, RoamingChangeCountry, SubscriptionEnds
]
CloudEvent = subscriptions.CloudEvent[NotificationEventType, CloudEventData]
Subscription = subscriptions.Subscription[
    SubscriptionEventType, CreateSubscriptionDetail
]
SubscriptionTypeAdapter: TypeAdapter[Subscription] = TypeAdapter(Subscription)
SubscriptionRequest = subscriptions.SubscriptionRequest[
    SubscriptionEventType, CreateSubscriptionDetail
]
