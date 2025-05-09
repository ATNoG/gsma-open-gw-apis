from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Union, Annotated

from pydantic import BaseModel, Field, RootModel

from .common import PhoneNumber, NetworkAccessIdentifier, Port


class L4sQueueType(Enum):
    non_l4s_queue = "non-l4s-queue"
    l4s_queue = "l4s-queue"
    mixed_queue = "mixed-queue"


class ServiceClass(Enum):
    microsoft_voice = "microsoft_voice"
    microsoft_audio_video = "microsoft_audio_video"
    real_time_interactive = "real_time_interactive"
    multimedia_streaming = "multimedia_streaming"
    broadcast_video = "broadcast_video"
    low_latency_data = "low_latency_data"
    high_throughput_data = "high_throughput_data"
    low_priority_data = "low_priority_data"
    standard = "standard"


QosProfileName = Annotated[
    str,
    Field(
        pattern=r"^[a-zA-Z0-9_.-]+$",
        min_length=3,
        max_length=256,
        description="A unique name for identifying a specific QoS profile.\nThis may follow different formats depending on the service providers implementation.\nSome options addresses:\n  - A UUID style string\n  - Support for predefined profile names like `QOS_E`, `QOS_S`, `QOS_M`, and `QOS_L`\n  - A searchable descriptive name",
        examples=["voice"],
    ),
]


class TimeUnitEnum(Enum):
    Days = "Days"
    Hours = "Hours"
    Minutes = "Minutes"
    Seconds = "Seconds"
    Milliseconds = "Milliseconds"
    Microseconds = "Microseconds"
    Nanoseconds = "Nanoseconds"


class QosProfileStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"


class RateUnitEnum(Enum):
    bps = "bps"
    kbps = "kbps"
    Mbps = "Mbps"
    Gbps = "Gbps"
    Tbps = "Tbps"


class Rate(BaseModel):
    value: Annotated[
        Optional[int],
        Field(ge=0, le=1024, description="Quantity of rate", examples=[10]),
    ] = None
    unit: Optional[RateUnitEnum] = None


class Duration(BaseModel):
    value: Annotated[
        Optional[int], Field(ge=1, description="Quantity of duration", examples=[12])
    ] = None
    unit: Optional[TimeUnitEnum] = None


class DeviceIpv4Addr1(BaseModel):
    publicAddress: IPv4Address
    privateAddress: IPv4Address
    publicPort: Optional[Port] = None


class DeviceIpv4Addr2(BaseModel):
    publicAddress: IPv4Address
    privateAddress: Optional[IPv4Address] = None
    publicPort: Port


class DeviceIpv4Addr(RootModel[Union[DeviceIpv4Addr1, DeviceIpv4Addr2]]):
    root: Annotated[
        Union[DeviceIpv4Addr1, DeviceIpv4Addr2],
        Field(
            description="The device should be identified by either the public (observed) IP address and port as seen by the application server, or the private (local) and any public (observed) IP addresses in use by the device (this information can be obtained by various means, for example from some DNS servers).\n\nIf the allocated and observed IP addresses are the same (i.e. NAT is not in use) then  the same address should be specified for both publicAddress and privateAddress.\n\nIf NAT64 is in use, the device should be identified by its publicAddress and publicPort, or separately by its allocated IPv6 address (field ipv6Address of the Device object)\n\nIn all cases, publicAddress must be specified, along with at least one of either privateAddress or publicPort, dependent upon which is known. In general, mobile devices cannot be identified by their public IPv4 address alone.",
            examples=[{"publicAddress": "203.0.113.0", "publicPort": 59765}],
        ),
    ]


class QosProfile(BaseModel):
    name: QosProfileName
    description: Annotated[
        Optional[str],
        Field(
            description="A description of the QoS profile.",
            examples=["QoS profile for video streaming"],
        ),
    ] = None
    status: QosProfileStatus
    targetMinUpstreamRate: Annotated[
        Optional[Rate],
        Field(
            description="This is the target minimum upload speed for the QoS profile.\nIt represents the minimum rate that the network attempts to deliver.\nPlease note that this is a target value—the network might not always be able to provide this rate under all conditions.\nIt helps ensure that applications like video calls or live streaming perform consistently.",
        ),
    ] = None
    maxUpstreamRate: Annotated[
        Optional[Rate], Field(description="The maximum best effort data")
    ] = None
    maxUpstreamBurstRate: Annotated[
        Optional[Rate],
        Field(
            description="When defined, this is the maximum upstream burst rate for the QoS profile, that will enable\nthe network to burst data at a higher rate than the maxUpstreamRate for a period of time.",
        ),
    ] = None
    targetMinDownstreamRate: Annotated[
        Optional[Rate],
        Field(
            description="This is the target maximum upload speed for the QoS profile.\nIt represents the maximum rate that the network attempts to deliver.\nPlease note that this is a target value—the network might not always be able to provide this rate under all conditions.\nIt helps ensure that applications like video calls or live streaming perform consistently.",
        ),
    ] = None
    maxDownstreamRate: Annotated[
        Optional[Rate], Field(description="The maximum best effort rate")
    ] = None
    maxDownstreamBurstRate: Annotated[
        Optional[Rate],
        Field(
            description="When defined, this is the maximum downstream burst rate for the QoS profile, that will enable\nthe network to burst data at a higher rate than the maxDownstreamRate for a period of time.\nThis can result in improved user experience when there is additional network capacity.\nFor instance, when a user is streaming a video, the network can burst data at a higher rate\nto fill the buffer, and then return to the maxUpstreamRate once the buffer is full.",
        ),
    ] = None
    minDuration: Annotated[
        Optional[Duration],
        Field(
            description="The shortest time period that this profile can be deployed.",
        ),
    ] = None
    maxDuration: Annotated[
        Optional[Duration],
        Field(
            description="The maximum time period that this profile can be deployed.\nOverall session duration must not exceed this value. This includes the initial requested duration plus any extensions.",
        ),
    ] = None
    priority: Annotated[
        Optional[int],
        Field(
            ge=1,
            le=100,
            description="Priority levels allow efficient resource allocation and ensure optimal performance\nfor various services in each technology, with the highest priority traffic receiving\npreferential treatment.\nThe lower value the higher priority.\nNot all access networks use the same priority range, so this priority will be\nscaled to the access network's priority range.",
            examples=[20],
        ),
    ] = None
    packetDelayBudget: Annotated[
        Optional[Duration],
        Field(
            description="The packet delay budget is the maximum allowable one-way latency between the customer's device\nand the gateway from the operator's network to other networks. By limiting the delay, the network\ncan provide an acceptable level of performance for various services, such as voice calls,\nvideo streaming, and data.\nThe end-to-end or round trip latency will be about two times this value plus the latency not controlled\nby the operator",
        ),
    ] = None
    jitter: Annotated[
        Optional[Duration],
        Field(
            description="The jitter requirement aims to limit the maximum variation in round-trip\npacket delay for the 99th percentile of traffic, following ITU Y.1540\nstandards. It considers only acknowledged packets in a session, which are\npackets that receive a confirmation of receipt from the recipient (e.g.,\nusing TCP). This requirement helps maintain consistent latency, essential\nfor real-time applications such as VoIP, video calls, and gaming.",
        ),
    ] = None
    packetErrorLossRate: Annotated[
        Optional[int],
        Field(
            ge=1,
            le=10,
            description="This field specifies the acceptable level of data loss during transmission.\nThe value is an exponent of 10, so a value of 3 means that up to 10⁻³, or 0.1%, of the\ndata packets may be lost. This setting is part of a broader system that categorizes\ndifferent types of network traffic (like phone calls, video streams, or data transfers)\nto ensure they perform reliably on the network.",
            examples=[3],
        ),
    ] = None
    l4sQueueType: Annotated[
        Optional[L4sQueueType],
        Field(
            description="\n**NOTE**: l4sQueueType is experimental and could change or be removed in a future release.\n\nSpecifies the type of queue for L4S (Low Latency, Low Loss, Scalable Throughput) traffic management. L4S is an advanced queue management approach designed to provide ultra-low latency and high throughput for internet traffic, particularly beneficial for interactive applications such as gaming, video conferencing, and virtual reality.\n\n**Queue Type Descriptions:**\n\n- **non-l4s-queue**:\n  A traditional queue used for legacy internet traffic that does not utilize L4S enhancements. It provides standard latency and throughput levels.\n\n- **l4s-queue**:\n  A dedicated queue optimized for L4S traffic, delivering ultra-low latency, low loss, and scalable throughput to support latency-sensitive applications.\n\n- **mixed-queue**:\n  A shared queue that can handle both L4S and traditional traffic, offering a balance between ultra-low latency for L4S flows and compatibility with non-L4S flows.",
        ),
    ] = None
    serviceClass: Annotated[
        Optional[ServiceClass],
        Field(
            description="\n**NOTE**: serviceClass is experimental and could change or be removed in a future release.\n\nThe name of a Service Class, representing a QoS Profile designed to provide optimized behavior for a specific application type. While DSCP values are commonly associated with Service Classes, their use may vary across network segments and may not be applied throughout the entire end-to-end QoS session. This aligns with the serviceClass concept used in HomeDevicesQoQ for consistent terminology.\n\nService classes define specific QoS behaviors that map to DSCP (Differentiated Services Code Point) values or Microsoft QoS traffic types.\n\nThe supported mappings are:\n1. Values aligned with the [RFC4594](https://datatracker.ietf.org/doc/html/rfc4594) guidelines for differentiated traffic classes.\n2. Microsoft [QOS_TRAFFIC_TYPE](https://learn.microsoft.com/en-us/windows/win32/api/qos2/ne-qos2-qos_traffic_type) values for Windows developers.\n\n**Supported Service Classes**:\n\n| Service Class Name    | DSCP Name | DSCP value (decimal) | DCSP value (binary) | Microsoft Value | Application Examples                                                 |\n|-----------------------|-----------|----------------------|---------------------|-----------------|----------------------------------------------------------------------|\n| Microsoft Voice       |    CS7    |          56          |        111000       |       4,5       | Microsoft QOSTrafficTypeVoice and QOSTrafficTypeControl              |\n| Microsoft Audio/Video |    CS5    |          40          |        101000       |       2,3       | Microsoft QOSTrafficTypeExcellentEffort and QOSTrafficTypeAudioVideo |\n| Real-Time Interactive |    CS4    |          32          |        100000       |                 | Video conferencing and Interactive gaming                            |\n| Multimedia Streaming  |    AF31   |          26          |        011010       |                 | Streaming video and audio on demand                                  |\n| Broadcast Video       |    CS3    |          24          |        011000       |                 | Broadcast TV & live events                                           |\n| Low-Latency Data      |    AF21   |          18          |        010010       |                 | Client/server transactions Web-based ordering                        |\n| High-Throughput Data  |    AF11   |          10          |        001010       |                 | Store and forward applications                                       |\n| Low-Priority Data     |    CS1    |           8          |        001000       |        1        | Any flow that has no BW assurance - also:                            |\n|                       |           |                      |                     |                 | Microsoft QOSTrafficTypeBackground                                   |\n| Standard              |  DF(CS0)  |           0          |        000000       |        0        | Undifferentiated applications - also:                                |\n|                       |           |                      |                     |                 | Microsoft QOSTrafficTypeBestEffort                                   |",
            examples=["real_time_interactive"],
        ),
    ] = None


class Device(BaseModel):
    phoneNumber: Optional[PhoneNumber] = None
    networkAccessIdentifier: Optional[NetworkAccessIdentifier] = None
    ipv4Address: Optional[DeviceIpv4Addr] = None
    ipv6Address: Optional[IPv6Address] = None


class QosProfileDeviceRequest(BaseModel):
    device: Optional[Device] = None
    name: Optional[QosProfileName] = None
    status: Optional[QosProfileStatus] = None
