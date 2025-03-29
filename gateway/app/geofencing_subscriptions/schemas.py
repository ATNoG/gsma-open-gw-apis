from __future__ import annotations

from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyUrl,
    BaseModel,
    Field,
    RootModel,
    ConfigDict,
    PositiveInt,
    confloat,
    conint,
    constr,
)


class ErrorInfo(BaseModel):
    status: int = Field(..., description="HTTP response status code.")
    code: str = Field(..., description="Code given to this error.")
    message: str = Field(..., description="Detailed error description.")


class Protocol(Enum):
    HTTP = "HTTP"
    MQTT3 = "MQTT3"
    MQTT5 = "MQTT5"
    AMQP = "AMQP"
    NATS = "NATS"
    KAFKA = "KAFKA"


class CredentialType(Enum):
    PLAIN = "PLAIN"
    ACCESSTOKEN = "ACCESSTOKEN"
    REFRESHTOKEN = "REFRESHTOKEN"


class SinkCredential(BaseModel):
    credentialType: CredentialType = Field(
        ..., description="The type of the credential."
    )


class PlainCredential(SinkCredential):
    identifier: str = Field(
        ..., description="The identifier might be an account or username."
    )
    secret: str = Field(
        ..., description="The secret might be a password or passphrase."
    )


class AccessTokenType(Enum):
    bearer = "bearer"


class AccessTokenCredential(SinkCredential):
    accessToken: str = Field(
        ...,
        description="REQUIRED. An access token is a previously acquired token granting access to the target resource.",
    )
    accessTokenExpiresUtc: datetime = Field(
        ...,
        description="REQUIRED. An absolute UTC instant at which the token shall be considered expired.",
    )
    accessTokenType: AccessTokenType = Field(
        ...,
        description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)).",
    )


class RefreshTokenCredential(SinkCredential):
    accessToken: str = Field(
        ...,
        description="REQUIRED. An access token is a previously acquired token granting access to the target resource.",
    )
    accessTokenExpiresUtc: datetime = Field(
        ...,
        description="REQUIRED. An absolute UTC instant at which the token shall be considered expired.",
    )
    accessTokenType: AccessTokenType = Field(
        ...,
        description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1)).",
    )
    refreshToken: str = Field(
        ...,
        description="REQUIRED. An refresh token credential used to acquire access tokens.",
    )
    refreshTokenEndpoint: AnyUrl = Field(
        ...,
        description="REQUIRED. A URL at which the refresh token can be traded for an access token.",
    )


class SubscriptionEventType(Enum):
    org_camaraproject_geofencing_subscriptions_v0_area_entered = (
        "org.camaraproject.geofencing-subscriptions.v0.area-entered"
    )
    org_camaraproject_geofencing_subscriptions_v0_area_left = (
        "org.camaraproject.geofencing-subscriptions.v0.area-left"
    )


class NotificationEventType(Enum):
    org_camaraproject_geofencing_subscriptions_v0_area_entered = (
        "org.camaraproject.geofencing-subscriptions.v0.area-entered"
    )
    org_camaraproject_geofencing_subscriptions_v0_area_left = (
        "org.camaraproject.geofencing-subscriptions.v0.area-left"
    )
    org_camaraproject_geofencing_subscriptions_v0_subscription_ends = (
        "org.camaraproject.geofencing-subscriptions.v0.subscription-ends"
    )


class Status(Enum):
    ACTIVATION_REQUESTED = "ACTIVATION_REQUESTED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class SubscriptionId(RootModel[str]):
    root: str = Field(
        ...,
        description="The unique identifier of the subscription in the scope of the subscription manager. When this information is contained within an event notification, this concept SHALL be referred as `subscriptionId` as per [Commonalities Event Notification Model](https://github.com/camaraproject/Commonalities/blob/main/documentation/API-design-guidelines.md#122-event-notification).",
        examples=["qs15-h556-rt89-1298"],
    )


class PhoneNumber(RootModel[constr(pattern=r"^\+[1-9][0-9]{4,14}$")]):
    root: str = Field(
        ...,
        pattern=r"^\+[1-9][0-9]{4,14}$",
        description="A public identifier addressing a telephone subscription. In mobile networks, it corresponds to the MSISDN (Mobile Station International Subscriber Directory Number). In order to be globally unique it has to be formatted in international format, according to E.164 standard, prefixed with '+'.",
        examples=["+123456789"],
    )


class NetworkAccessIdentifier(RootModel[str]):
    root: str = Field(
        ...,
        description="A public identifier addressing a subscription in a mobile network. In 3GPP terminology, it corresponds to the GPSI formatted with the External Identifier ({Local Identifier}@{Domain Identifier}). Unlike the telephone number, the network access identifier is not subjected to portability ruling in force, and is individually managed by each operator.",
        examples=["123456789@domain.com"],
    )


class SingleIpv4Addr(RootModel[IPv4Address]):
    root: IPv4Address = Field(
        ...,
        description="A single IPv4 address with no subnet mask.",
        examples=["84.125.93.10"],
    )


class Port(RootModel[conint(ge=0, le=65535)]):
    root: int = Field(..., ge=0, le=65535, description="TCP or UDP port number.")


class DeviceIpv6Address(RootModel[IPv6Address]):
    root: IPv6Address = Field(
        ...,
        description="The device should be identified by the observed IPv6 address, or by any single IPv6 address from within the subnet allocated to the device (e.g. adding ::0 to the /64 prefix).\n",
        examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
    )


class AreaType(Enum):
    CIRCLE = "CIRCLE"


class Latitude(RootModel[confloat(ge=-90.0, le=90.0)]):
    root: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude component of a location.",
        examples=[50.735851],
    )


class Longitude(RootModel[confloat(ge=-180.0, le=180.0)]):
    root: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude component of location.",
        examples=[7.10066],
    )


class Specversion(Enum):
    field_1_0 = "1.0"


class Datacontenttype(Enum):
    application_json = "application/json"


class Source(RootModel[constr(min_length=1)]):
    root: str = Field(
        ...,
        min_length=1,
        description="Identifies the context in which an event happened - be a non-empty `URI-reference` like:\n- URI with a DNS authority:\n  * https://github.com/cloudevents\n  * mailto:cncf-wg-serverless@lists.cncf.io\n- Universally-unique URN with a UUID:\n  * urn:uuid:6e8bc430-9c3a-11d9-9669-0800200c9a66\n- Application-specific identifier:\n  * /cloudevents/spec/pull/123\n  * 1-555-123-4567\n",
        examples=["https://notificationSendServer12.supertelco.com"],
    )


class DateTime(RootModel[datetime]):
    root: datetime = Field(
        ...,
        description="Timestamp of when the occurrence happened. Must adhere to RFC 3339.",
        examples=["2018-04-05T17:31:00Z"],
    )


class TerminationReason(Enum):
    MAX_EVENTS_REACHED = "MAX_EVENTS_REACHED"
    NETWORK_TERMINATED = "NETWORK_TERMINATED"
    SUBSCRIPTION_UNPROCESSABLE = "SUBSCRIPTION_UNPROCESSABLE"
    SUBSCRIPTION_EXPIRED = "SUBSCRIPTION_EXPIRED"
    SUBSCRIPTION_DELETED = "SUBSCRIPTION_DELETED"
    ACCESS_TOKEN_EXPIRED = "ACCESS_TOKEN_EXPIRED"


class Method(Enum):
    POST = "POST"


class HTTPSettings(BaseModel):
    headers: Optional[Dict[str, str]] = Field(
        None,
        description="A set of key/value pairs that is copied into the HTTP request as custom headers.\n\nNOTE: Use/Applicability of this concept has not been discussed in Commonalities under the scope of Meta Release v0.4. When required by an API project as an option to meet a UC/Requirement, please generate an issue for Commonalities discussion about it.",
    )
    method: Optional[Method] = Field(
        None, description="The HTTP method to use for sending the message."
    )


class MQTTSettings(BaseModel):
    topicName: str
    qos: Optional[int] = None
    retain: Optional[bool] = None
    expiry: Optional[int] = None
    userProperties: Optional[Dict[str, Any]] = None


class SenderSettlementMode(Enum):
    settled = "settled"
    unsettled = "unsettled"


class AMQPSettings(BaseModel):
    address: Optional[str] = None
    linkName: Optional[str] = None
    senderSettlementMode: Optional[SenderSettlementMode] = None
    linkProperties: Optional[Dict[str, str]] = None


class ApacheKafkaSettings(BaseModel):
    topicName: str
    partitionKeyExtractor: Optional[str] = None
    clientId: Optional[str] = None
    ackMode: Optional[int] = None


class NATSSettings(BaseModel):
    subject: str


class SubscriptionAsync(BaseModel):
    id: Optional[SubscriptionId] = None


class DeviceIpv4Addr1(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: SingleIpv4Addr
    publicPort: Optional[Port] = None


class DeviceIpv4Addr2(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: Optional[SingleIpv4Addr] = None
    publicPort: Port


class DeviceIpv4Addr(RootModel[Union[DeviceIpv4Addr1, DeviceIpv4Addr2]]):
    root: Union[DeviceIpv4Addr1, DeviceIpv4Addr2] = Field(
        ...,
        description="The device should be identified by either the public (observed) IP address and port as seen by the application server, or the private (local) and any public (observed) IP addresses in use by the device (this information can be obtained by various means, for example from some DNS servers).\n\nIf the allocated and observed IP addresses are the same (i.e. NAT is not in use) then  the same address should be specified for both publicAddress and privateAddress.\n\nIf NAT64 is in use, the device should be identified by its publicAddress and publicPort, or separately by its allocated IPv6 address (field ipv6Address of the Device object)\n\nIn all cases, publicAddress must be specified, along with at least one of either privateAddress or publicPort, dependent upon which is known. In general, mobile devices cannot be identified by their public IPv4 address alone.\n",
        examples=[{"publicAddress": "84.125.93.10", "publicPort": 59765}],
    )


class Area(BaseModel):
    areaType: AreaType


class Point(BaseModel):
    latitude: Latitude
    longitude: Longitude


class CloudEvent(BaseModel):
    id: str = Field(
        ...,
        description="Identifier of this event, that must be unique in the source context.",
    )
    source: Source
    type: NotificationEventType
    specversion: Specversion = Field(
        ...,
        description="Version of the specification to which this event conforms (must be 1.0 if it conforms to cloudevents 1.0.2 version).",
    )
    datacontenttype: Optional[Datacontenttype] = Field(
        None,
        description='media-type that describes the event payload encoding, must be "application/json" for CAMARA APIs',
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Event details payload described in each CAMARA API and referenced by its type.",
    )
    time: DateTime


class Device(BaseModel):
    phoneNumber: Optional[PhoneNumber] = None
    networkAccessIdentifier: Optional[NetworkAccessIdentifier] = None
    ipv4Address: Optional[DeviceIpv4Addr] = None
    ipv6Address: Optional[DeviceIpv6Address] = None


class Circle(Area):
    center: Point
    radius: int = Field(
        ...,
        ge=1,
        le=200000,
        description="Expected accuracy for the subscription event of device location, in meters from `center`.\nNote: The area surface could be restricted locally depending on regulations. Implementations may enforce a larger minimum radius (e.g. 1000 meters).\n",
    )


class AreaLeft(BaseModel):
    device: Device
    area: Area
    subscriptionId: SubscriptionId


class AreaEntered(BaseModel):
    device: Device
    area: Area
    subscriptionId: SubscriptionId


class SubscriptionEnds(BaseModel):
    device: Device
    area: Area
    terminationReason: TerminationReason
    terminationDescription: Optional[str] = Field(
        None, description="Explanation why a subscription ended or had to end."
    )
    subscriptionId: SubscriptionId


class SubscriptionDetail(BaseModel):
    device: Device
    area: Area


class Config(BaseModel):
    subscriptionDetail: SubscriptionDetail
    subscriptionExpireTime: Optional[datetime] = Field(
        None,
        description="The subscription expiration time (in date-time format) requested by the API consumer.",
        examples=["2023-01-17T13:18:23.682Z"],
    )
    subscriptionMaxEvents: Optional[int] = Field(
        None,
        ge=1,
        description="Identifies the maximum number of event reports to be generated (>=1) requested by the API consumer - Once this number is reached, the subscription ends.\nNote on combined usage of `initialEvent` and `subscriptionMaxEvents`:\nIf an event is triggered following `initialEvent` set to `true`, this event will be counted towards `subscriptionMaxEvents`.\n",
        examples=[5],
    )
    initialEvent: Optional[bool] = Field(
        None,
        description="Set to `true` by API consumer if consumer wants to get an event as soon as the subscription is created and current situation reflects event request.\nExample: Consumer request area entered event. If consumer sets initialEvent to true and device is already in the geofence, an event is triggered.\n",
    )


class Subscription(BaseModel):
    protocol: Protocol
    sink: str = Field(
        ...,
        description="The address to which events shall be delivered using the selected protocol.",
        examples=["https://endpoint.example.com/sink"],
    )
    sinkCredential: Optional[SinkCredential] = None
    types: List[SubscriptionEventType] = Field(
        ...,
        description="Camara Event types eligible to be delivered by this subscription.\n",
    )
    config: Config
    id: str = Field(
        ...,
        description="The unique identifier of the subscription in the scope of the subscription manager. When this information is contained within an event notification, this concept SHALL be referred as `subscriptionId` as per [Commonalities Event Notification Model](https://github.com/camaraproject/Commonalities/blob/main/documentation/API-design-guidelines.md#122-event-notification).",
        examples=["1119920371"],
    )
    startsAt: datetime = Field(
        ..., description="Date when the event subscription will begin/began."
    )
    expiresAt: Optional[datetime] = Field(
        None,
        description="Date when the event subscription will expire. Only provided when `subscriptionExpireTime` is indicated by API client or Telco Operator has a specific policy about that.",
    )
    status: Optional[Status] = Field(
        None,
        description="Current status of the subscription - Management of Subscription State engine is not mandatory for now. Note not all statuses may be considered to be implemented. Details:\n  - `ACTIVATION_REQUESTED`: Subscription creation (POST) is triggered but subscription creation process is not finished yet.\n  - `ACTIVE`: Subscription creation process is completed. Subscription is fully operative.\n  - `INACTIVE`: Subscription is temporarily inactive, but its workflow logic is not deleted.\n  - `EXPIRED`: Subscription is ended (no longer active). This status applies when subscription is ended due to `SUBSCRIPTION_EXPIRED` or `ACCESS_TOKEN_EXPIRED` event.\n  - `DELETED`: Subscription is ended as deleted (no longer active). This status applies when subscription information is kept (i.e. subscription workflow is no longer active but its meta-information is kept).",
    )


class HTTPSubscriptionResponse(Subscription):
    protocolSettings: Optional[HTTPSettings] = None


class MQTTSubscriptionResponse(Subscription):
    protocolSettings: Optional[MQTTSettings] = None


class AMQPSubscriptionResponse(Subscription):
    protocolSettings: Optional[AMQPSettings] = None


class ApacheKafkaSubscriptionResponse(Subscription):
    protocolSettings: Optional[ApacheKafkaSettings] = None


class NATSSubscriptionResponse(Subscription):
    protocolSettings: Optional[NATSSettings] = None


class SubscriptionRequest(BaseModel):
    protocol: Protocol
    sink: str = Field(
        ...,
        description="The address to which events shall be delivered using the selected protocol.",
        examples=["https://endpoint.example.com/sink"],
    )
    sinkCredential: Optional[SinkCredential] = None
    types: List[SubscriptionEventType] = Field(
        ...,
        description="Camara Event types which are eligible to be delivered by this subscription.\nNote: As of now we enforce to have only event type per subscription.\n",
        max_length=1,
        min_length=1,
    )
    config: Config


class HTTPSubscriptionRequest(SubscriptionRequest):
    protocolSettings: Optional[HTTPSettings] = None


class MQTTSubscriptionRequest(SubscriptionRequest):
    protocolSettings: Optional[MQTTSettings] = None


class AMQPSubscriptionRequest(SubscriptionRequest):
    protocolSettings: Optional[AMQPSettings] = None


class ApacheKafkaSubscriptionRequest(SubscriptionRequest):
    protocolSettings: Optional[ApacheKafkaSettings] = None


class NATSSubscriptionRequest(SubscriptionRequest):
    protocolSettings: Optional[NATSSettings] = None


#######
# Nef #
#######


class MonitoringType(Enum):
    LOCATION_REPORTING = "LOCATION_REPORTING"
    LOSS_OF_CONNECTIVITY = "LOSS_OF_CONNECTIVITY"
    UE_REACHABILITY = "UE_REACHABILITY"


class ReachabilityType(Enum):
    SMS = "SMS"
    DATA = "DATA"


class MonitoringEventSubscriptionCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    externalId: Optional[str] = Field(
        default=None,
        description="Globally unique identifier containing a Domain Identifier and a Local Identifier. \\<Local Identifier\\>@\\<Domain Identifier\\>",
        title="Externalid",
    )
    notificationDestination: Optional[AnyUrl] = Field(
        default=None,
        description="Reference resource (URL) identifying service consumer's endpoint, in order to receive the asynchronous notification.",
        title="Notificationdestination",
    )
    monitoringType: MonitoringType
    maximumNumberOfReports: Optional[int] = Field(
        default=None,
        ge=1,
        description="Identifies the maximum number of event reports to be generated. Value 1 makes the Monitoring Request a One-time Request",
        title="Maximumnumberofreports",
    )
    monitorExpireTime: Optional[datetime] = Field(
        default=None,
        description="Identifies the absolute time at which the related monitoring event request is considered to expire",
        title="Monitorexpiretime",
    )
    maximumDetectionTime: Optional[PositiveInt] = Field(
        default=None,
        description='If monitoringType is "LOSS_OF_CONNECTIVITY", this parameter may be included to identify the maximum period of time after which the UE is considered to be unreachable.',
        title="Maximumdetectiontime",
    )
    reachabilityType: Optional[ReachabilityType] = Field(
        default=None,
        description='If monitoringType is "UE_REACHABILITY", this parameter shall be included to identify whether the request is for "Reachability for SMS" or "Reachability for Data"',
    )


class MonitoringEventSubscription(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    externalId: Optional[str] = Field(
        default=None,
        description="Globally unique identifier containing a Domain Identifier and a Local Identifier. \\<Local Identifier\\>@\\<Domain Identifier\\>",
        title="Externalid",
    )
    notificationDestination: Optional[AnyUrl] = Field(
        default=None,
        description="Reference resource (URL) identifying service consumer's endpoint, in order to receive the asynchronous notification.",
        title="Notificationdestination",
    )
    monitoringType: MonitoringType
    maximumNumberOfReports: Optional[int] = Field(
        default=None,
        ge=1,
        description="Identifies the maximum number of event reports to be generated. Value 1 makes the Monitoring Request a One-time Request",
        title="Maximumnumberofreports",
    )
    monitorExpireTime: Optional[datetime] = Field(
        None,
        description="Identifies the absolute time at which the related monitoring event request is considered to expire",
        title="Monitorexpiretime",
    )
    maximumDetectionTime: Optional[PositiveInt] = Field(
        default=None,
        description='If monitoringType is "LOSS_OF_CONNECTIVITY", this parameter may be included to identify the maximum period of time after which the UE is considered to be unreachable.',
        title="Maximumdetectiontime",
    )
    reachabilityType: Optional[ReachabilityType] = Field(
        default=None,
        description='If monitoringType is "UE_REACHABILITY", this parameter shall be included to identify whether the request is for "Reachability for SMS" or "Reachability for Data"',
    )
    link: Optional[AnyUrl] = Field(
        default=None,
        description="String identifying a referenced resource. This is also returned as a location header in 201 Created Response",
        title="Link",
    )
    ipv4Addr: Optional[str] = Field(
        default=None, description="String identifying an Ipv4 address", title="Ipv4Addr"
    )


class SupportedGADShapes(Enum):
    POINT = "POINT"


class GeographicalCoordinates(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    lon: float = Field(..., ge=-180.0, le=180.0, title="Lon")
    lat: float = Field(..., ge=-90.0, le=90.0, title="Lat")


class GeoPoint(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    shape: SupportedGADShapes
    point: GeographicalCoordinates


class GeographicArea(RootModel[GeoPoint]):
    root: GeoPoint = Field(
        ...,
        description="Geographic area specified by different shape.",
        title="GeographicArea",
    )


class LocationInfo(BaseModel):
    geographicArea: Optional[GeographicArea] = None


class MonitoringEventReport(BaseModel):
    locationInfo: Optional[LocationInfo] = None
    monitoringType: MonitoringType


class MonitoringNotification(BaseModel):
    monitoringEventReports: Optional[List[MonitoringEventReport]] = Field(
        None,
        description="Monitoring event reports.",
        min_length=1,
        title="Monitoringeventreports",
    )
