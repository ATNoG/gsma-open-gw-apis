from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from datetime import datetime

from pydantic import AnyUrl, BaseModel, Field


class SubscriptionStatus(str, Enum):
    ACTIVATION_REQUESTED = "ACTIVATION_REQUESTED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class Protocol(str, Enum):
    HTTP = "HTTP"
    MQTT3 = "MQTT3"
    MQTT5 = "MQTT5"
    AMQP = "AMQP"
    NATS = "NATS"
    KAFKA = "KAFKA"


class CredentialType(str, Enum):
    PLAIN = "PLAIN"
    ACCESSTOKEN = "ACCESSTOKEN"
    REFRESHTOKEN = "REFRESHTOKEN"


class SinkCredential(BaseModel):
    credentialType: Annotated[
        CredentialType, Field(description="The type of the credential.")
    ]


class PlainCredential(SinkCredential):
    identifier: Annotated[
        str, Field(description="The identifier might be an account or username.")
    ]
    secret: Annotated[
        str, Field(description="The secret might be a password or passphrase.")
    ]


class AccessTokenType(str, Enum):
    bearer = "bearer"


class AccessTokenCredential(SinkCredential):
    accessToken: Annotated[
        str,
        Field(
            description="REQUIRED. An access token is a previously acquired token granting access to the target resource."
        ),
    ]
    accessTokenExpiresUtc: Annotated[
        datetime,
        Field(
            description="REQUIRED. An absolute UTC instant at which the token shall be considered expired."
        ),
    ]
    accessTokenType: Annotated[
        AccessTokenType,
        Field(
            description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1))."
        ),
    ]


class RefreshTokenCredential(SinkCredential):
    accessToken: Annotated[
        str,
        Field(
            description="REQUIRED. An access token is a previously acquired token granting access to the target resource."
        ),
    ]
    accessTokenExpiresUtc: Annotated[
        datetime,
        Field(
            description="REQUIRED. An absolute UTC instant at which the token shall be considered expired."
        ),
    ]
    accessTokenType: Annotated[
        AccessTokenType,
        Field(
            description="REQUIRED. Type of the access token (See [OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-7.1))."
        ),
    ]
    refreshToken: Annotated[
        str,
        Field(
            description="REQUIRED. A refresh token credential used to acquire access tokens."
        ),
    ]
    refreshTokenEndpoint: Annotated[
        AnyUrl,
        Field(
            description="REQUIRED. A URL at which the refresh token can be traded for an access token."
        ),
    ]


Source = Annotated[
    str,
    Field(
        min_length=1,
        description="Identifies the context in which an event happened - be a non-empty `URI-reference` like:\n- URI with a DNS authority:\n  * https://github.com/cloudevents\n  * mailto:cncf-wg-serverless@lists.cncf.io\n- Universally-unique URN with a UUID:\n  * urn:uuid:6e8bc430-9c3a-11d9-9669-0800200c9a66\n- Application-specific identifier:\n  * /cloudevents/spec/pull/123\n  * 1-555-123-4567\n",
        examples=["https://notificationSendServer12.supertelco.com"],
    ),
]


class Specversion(str, Enum):
    field_1_0 = "1.0"


class Datacontenttype(str, Enum):
    application_json = "application/json"


DateTime = Annotated[
    datetime,
    Field(
        description="Timestamp of when the occurrence happened. Must adhere to RFC 3339.",
        examples=["2018-04-05T17:31:00Z"],
    ),
]


class Method(str, Enum):
    POST = "POST"


class HTTPSettings(BaseModel):
    headers: Annotated[
        Optional[Dict[str, str]],
        Field(
            description="A set of key/value pairs that is copied into the HTTP request as custom headers.\n\nNOTE: Use/Applicability of this concept has not been discussed in Commonalities under the scope of Meta Release v0.4. When required by an API project as an option to meet a UC/Requirement, please generate an issue for Commonalities discussion about it.",
        ),
    ] = None
    method: Annotated[
        Optional[Method],
        Field(description="The HTTP method to use for sending the message."),
    ] = None


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


SubscriptionId = Annotated[
    str,
    Field(
        description="The unique identifier of the subscription in the scope of the subscription manager. When this information is contained within an event notification, this concept SHALL be referred as `subscriptionId` as per [Commonalities Event Notification Model](https://github.com/camaraproject/Commonalities/blob/main/documentation/API-design-guidelines.md#122-event-notification).",
        examples=["qs15-h556-rt89-1298"],
    ),
]


class SubscriptionAsync(BaseModel):
    id: Optional[SubscriptionId] = None


class TerminationReason(str, Enum):
    MAX_EVENTS_REACHED = "MAX_EVENTS_REACHED"
    NETWORK_TERMINATED = "NETWORK_TERMINATED"
    SUBSCRIPTION_UNPROCESSABLE = "SUBSCRIPTION_UNPROCESSABLE"
    SUBSCRIPTION_EXPIRED = "SUBSCRIPTION_EXPIRED"
    SUBSCRIPTION_DELETED = "SUBSCRIPTION_DELETED"
    ACCESS_TOKEN_EXPIRED = "ACCESS_TOKEN_EXPIRED"


class CloudEvent[NotificationEventType: str, CloudEventData](BaseModel):
    id: Annotated[
        str,
        Field(
            description="Identifier of this event, that must be unique in the source context."
        ),
    ]

    source: Source
    type: NotificationEventType

    specversion: Annotated[
        Specversion,
        Field(
            description="Version of the specification to which this event conforms (must be 1.0 if it conforms to cloudevents 1.0.2 version).",
        ),
    ] = Specversion.field_1_0

    datacontenttype: Optional[
        Annotated[
            Datacontenttype,
            Field(
                description='media-type that describes the event payload encoding, must be "application/json" for CAMARA APIs',
            ),
        ]
    ] = Datacontenttype.application_json

    data: Annotated[
        CloudEventData,
        Field(
            description="Event details payload described in each CAMARA API and referenced by its type."
        ),
    ]

    time: DateTime


class SubscriptionConfig[SubscriptionDetails](BaseModel):
    subscriptionDetail: SubscriptionDetails
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
            description="Set to `true` by API consumer if consumer wants to get an event as soon as the subscription is created and current situation reflects event request.Up to API project decision to keep it.\nExample: Consumer request Roaming event. If consumer sets initialEvent to true and device is in roaming situation, an event is triggered\nUp to API project decision to keep it.",
        ),
    ] = None


class BaseSubscription[SubscriptionEventType: str, SubscriptionDetails](BaseModel):
    sink: Annotated[
        str,
        Field(
            description="The address to which events shall be delivered using the selected protocol.",
            examples=["https://endpoint.example.com/sink"],
        ),
    ]

    sinkCredential: Optional[SinkCredential] = None

    types: Annotated[
        List[SubscriptionEventType],
        Field(
            description="Camara Event types eligible to be delivered by this subscription.\n"
        ),
    ]

    config: SubscriptionConfig[SubscriptionDetails]

    id: SubscriptionId

    startsAt: Annotated[
        datetime,
        Field(description="Date when the event subscription will begin/began."),
    ]

    expiresAt: Optional[
        Annotated[
            datetime,
            Field(
                description="Date when the event subscription will expire. Only provided when `subscriptionExpireTime` is indicated by API client or Telco Operator has a specific policy about that."
            ),
        ]
    ] = None

    status: Optional[
        Annotated[
            SubscriptionStatus,
            Field(
                description="Current status of the subscription - Management of Subscription State engine is not mandatory for now. Note not all statuses may be considered to be implemented. Details:\n  - `ACTIVATION_REQUESTED`: Subscription creation (POST) is triggered but subscription creation process is not finished yet.\n  - `ACTIVE`: Subscription creation process is completed. Subscription is fully operative.\n  - `INACTIVE`: Subscription is temporarily inactive, but its workflow logic is not deleted.\n  - `EXPIRED`: Subscription is ended (no longer active). This status applies when subscription is ended due to `SUBSCRIPTION_EXPIRED` or `ACCESS_TOKEN_EXPIRED` event.\n  - `DELETED`: Subscription is ended as deleted (no longer active). This status applies when subscription information is kept (i.e. subscription workflow is no longer active but its meta-information is kept)."
            ),
        ]
    ] = None


class HTTPSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    BaseSubscription[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.HTTP]
    protocolSettings: Optional[HTTPSettings] = None


class MQTTSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    BaseSubscription[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Union[Literal[Protocol.MQTT3], Literal[Protocol.MQTT5]]
    protocolSettings: Optional[MQTTSettings] = None


class AMQPSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    BaseSubscription[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.AMQP]
    protocolSettings: Optional[AMQPSettings] = None


class ApacheKafkaSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    BaseSubscription[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.KAFKA]
    protocolSettings: Optional[ApacheKafkaSettings] = None


class NATSSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    BaseSubscription[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.NATS]
    protocolSettings: Optional[NATSSettings] = None


type Subscription[SubscriptionEventType: str, SubscriptionDetail] = Annotated[
    Union[
        HTTPSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
        MQTTSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
        AMQPSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
        ApacheKafkaSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
        NATSSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
    ],
    Field(discriminator="protocol"),
]


class SubscriptionRequestBase[SubscriptionEventType: str, SubscriptionDetail](
    BaseModel
):
    sink: Annotated[
        str,
        Field(
            description="The address to which events shall be delivered using the selected protocol.",
            examples=["https://endpoint.example.com/sink"],
        ),
    ]
    sinkCredential: Optional[SinkCredential] = None
    types: Annotated[
        List[SubscriptionEventType],
        Field(
            description="Camara Event types which are eligible to be delivered by this subscription.\nNote: As of now we enforce to have only event type per subscription.",
            max_length=1,
            min_length=1,
        ),
    ]
    config: SubscriptionConfig[SubscriptionDetail]


class HTTPSubscriptionRequest[SubscriptionEventType: str, SubscriptionDetail](
    SubscriptionRequestBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.HTTP]
    protocolSettings: Optional[HTTPSettings] = None


class MQTTSubscriptionRequest[SubscriptionEventType: str, SubscriptionDetail](
    SubscriptionRequestBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Union[Literal[Protocol.MQTT3], Literal[Protocol.MQTT5]]
    protocolSettings: Optional[MQTTSettings] = None


class AMQPSubscriptionRequest[SubscriptionEventType: str, SubscriptionDetail](
    SubscriptionRequestBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.AMQP]
    protocolSettings: Optional[AMQPSettings] = None


class ApacheKafkaSubscriptionRequest[SubscriptionEventType: str, SubscriptionDetail](
    SubscriptionRequestBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.KAFKA]
    protocolSettings: Optional[ApacheKafkaSettings] = None


class NATSSubscriptionRequest[SubscriptionEventType: str, SubscriptionDetail](
    SubscriptionRequestBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.NATS]
    protocolSettings: Optional[NATSSettings] = None


type SubscriptionRequest[SubscriptionEventType: str, SubscriptionDetail] = Annotated[
    Union[
        HTTPSubscriptionRequest[SubscriptionEventType, SubscriptionDetail],
        MQTTSubscriptionRequest[SubscriptionEventType, SubscriptionDetail],
        AMQPSubscriptionRequest[SubscriptionEventType, SubscriptionDetail],
        ApacheKafkaSubscriptionRequest[SubscriptionEventType, SubscriptionDetail],
        NATSSubscriptionRequest[SubscriptionEventType, SubscriptionDetail],
    ],
    Field(discriminator="protocol"),
]
