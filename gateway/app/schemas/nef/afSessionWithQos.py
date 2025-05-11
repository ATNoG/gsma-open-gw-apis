# Types for Nnef_AFsessionWithQoS defined in TS 29.122

from ipaddress import IPv4Address, IPv6Address
from typing import Optional, List
from typing_extensions import Annotated
from pydantic import BaseModel, Field

from .commonData import (
    IpAddr,
    MacAddr48,
    Port,
    SponsorInformation,
    SupportedFeatures,
    Dnn,
    Snssai,
    Link,
    ExternalGroupId,
    Gpsi,
    FlowInfo,
    EthFlowDescription,
    MultiModalId,
    ProtocolDescription,
    AlternativeServiceRequirementsData,
    UsageThreshold,
    DurationSec,
    BitRate,
    TscQosRequirement,
    UplinkDownlinkSupport,
    TemporalInValidity,
    WebsockNotifConfig,
    UserPlaneEvent,
    MediaType,
    PacketDelBudget,
    RttFlowReference,
    PduSetQosPara,
    DurationMilliSec,
    QosMonitoringInformation,
    AverWindow,
    EventsSubscReqData,
    ServAuthInfo,
    AccumulatedUsage,
    PlmnIdNid,
    Uinteger,
    PdvMonitoringReport,
    RatType,
    BatOffsetInfo,
)


class EthFlowInfo(BaseModel):
    flowId: Annotated[
        int, Field(..., description="Indicates the Ethernet flow identifier.")
    ]
    ethFlowDescriptions: Annotated[
        Optional[List[EthFlowDescription]],
        Field(
            description="Indicates the packet filters of the Ethernet flow. It shall contain UL and/or DL Ethernet flow description.",
            max_length=2,
            min_length=1,
        ),
    ] = None


class UeAddInfo(BaseModel):
    ueIpAddr: Optional[IpAddr] = None
    portNumber: Optional[Port] = None


class AsSessionMediaComponent(BaseModel):
    flowInfos: Annotated[
        Optional[List[FlowInfo]],
        Field(
            description="Contains the IP data flow(s) description for a single-modal data flow.",
            min_length=1,
        ),
    ] = None
    qosReference: Optional[str] = None
    disUeNotif: Optional[bool] = None
    altSerReqs: Annotated[
        Optional[List[str]],
        Field(
            description="Contains alternative service requirements that include QoS references set",
            min_length=1,
        ),
    ] = None
    altSerReqsData: Annotated[
        Optional[List[AlternativeServiceRequirementsData]],
        Field(
            description="Contains alternative service requirements that include individual QoS parameter sets.",
            min_length=1,
        ),
    ] = None
    marBwDl: Optional[BitRate] = None
    marBwUl: Optional[BitRate] = None
    medCompN: int
    medType: Optional[MediaType] = None
    mirBwDl: Optional[BitRate] = None
    mirBwUl: Optional[BitRate] = None
    rTLatencyInd: Annotated[
        Optional[bool],
        Field(
            description='Indicates the service data flow needs to meet the Round-Trip (RT) latency requirement of the service, when it is included and set to "true". The default value is "false" if omitted.',
        ),
    ] = None
    pdb: Optional[PacketDelBudget] = None
    rTLatencyIndCorreId: Optional[RttFlowReference] = None
    pduSetQosDl: Optional[PduSetQosPara] = None
    pduSetQosUl: Optional[PduSetQosPara] = None
    l4sInd: Optional[UplinkDownlinkSupport] = None
    protoDescDl: Optional[ProtocolDescription] = None
    protoDescUl: Optional[ProtocolDescription] = None
    periodUl: Optional[DurationMilliSec] = None
    periodDl: Optional[DurationMilliSec] = None
    evSubsc: Optional[EventsSubscReqData] = None


class AsSessionWithQoSSubscription(BaseModel):
    self: Optional[Link] = None
    supportedFeatures: Optional[SupportedFeatures] = None
    dnn: Optional[Dnn] = None
    snssai: Optional[Snssai] = None
    notificationDestination: Link
    exterAppId: Annotated[
        Optional[str],
        Field(description="Identifies the external Application Identifier."),
    ] = None
    extGroupId: Optional[ExternalGroupId] = None
    gpsi: Optional[Gpsi] = None
    flowInfo: Annotated[
        Optional[List[FlowInfo]],
        Field(description="Describe the data flow which requires QoS.", min_length=1),
    ] = None
    ethFlowInfo: Annotated[
        Optional[List[EthFlowDescription]],
        Field(description="Identifies Ethernet packet flows.", min_length=1),
    ] = None
    enEthFlowInfo: Annotated[
        Optional[List[EthFlowInfo]],
        Field(
            description="Identifies the Ethernet flows which require QoS. Each Ethernet flow consists of a flow idenifer and the corresponding UL and/or DL flows.",
            min_length=1,
        ),
    ] = None
    listUeAddrs: Annotated[
        Optional[List[UeAddInfo]],
        Field(description="Identifies the list of UE address.", min_length=1),
    ] = None
    multiModalId: Optional[MultiModalId] = None
    protoDescUl: Optional[ProtocolDescription] = None
    protoDescDl: Optional[ProtocolDescription] = None
    qosReference: Annotated[
        Optional[str], Field(description="Identifies a pre-defined QoS information")
    ] = None
    altQoSReferences: Annotated[
        Optional[List[str]],
        Field(
            description="Identifies an ordered list of pre-defined QoS information. The lower the index of the array for a given entry, the higher the priority.",
            min_length=1,
        ),
    ] = None
    altQosReqs: Annotated[
        Optional[List[AlternativeServiceRequirementsData]],
        Field(
            description="Identifies an ordered list of alternative service requirements that include individual QoS parameter sets. The lower the index of the array for a given entry, the higher the priority.",
            min_length=1,
        ),
    ] = None
    disUeNotif: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether the QoS flow parameters signalling to the UE when the SMF is notified by the NG-RAN of changes in the fulfilled QoS situation is disabled (true) or not (false). Default value is false. The fulfilled situation is either the QoS profile or an Alternative QoS Profile.",
        ),
    ] = None
    ueIpv4Addr: Optional[IPv4Address] = None
    ipDomain: Optional[str] = None
    ueIpv6Addr: Optional[IPv6Address] = None
    macAddr: Optional[MacAddr48] = None
    usageThreshold: Optional[UsageThreshold] = None
    sponsorInfo: Optional[SponsorInformation] = None
    qosMonInfo: Optional[QosMonitoringInformation] = None
    pdvMon: Optional[QosMonitoringInformation] = None
    qosDuration: Optional[DurationSec] = None
    qosInactInt: Optional[DurationSec] = None
    directNotifInd: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether the direct event notification is requested (true) or not (false) for the provided and/or previously provided QoS monitoring parameter(s).",
        ),
    ] = None
    tscQosReq: Optional[TscQosRequirement] = None
    l4sInd: Optional[UplinkDownlinkSupport] = None
    requestTestNotification: Annotated[
        Optional[bool],
        Field(
            description="Set to true by the SCS/AS to request the SCEF to send a test notification as defined in clause 5.2.5.3. Set to false or omitted otherwise.",
        ),
    ] = None
    tempInValidity: Optional[TemporalInValidity] = None
    websockNotifConfig: Optional[WebsockNotifConfig] = None
    events: Annotated[
        Optional[List[UserPlaneEvent]],
        Field(
            description="Represents the list of user plane event(s) to which the SCS/AS requests to subscribe to.",
            min_length=1,
        ),
    ] = None
    multiModDatFlows: Annotated[
        Optional[dict[str, AsSessionMediaComponent]],
        Field(
            description="Contains media component data for a single-modal data flow(s). The key of the map is the medCompN attribute.",
        ),
    ] = None
    pduSetQosDl: Optional[PduSetQosPara] = None
    pduSetQosUl: Optional[PduSetQosPara] = None
    rTLatencyInd: Annotated[
        Optional[bool],
        Field(
            description='Indicates the service data flow needs to meet the Round-Trip (RT) latency requirement of the service, when it is included and set to "true". The default value is "false" if omitted.',
        ),
    ] = None
    pdb: Optional[PacketDelBudget] = None
    periodUl: Optional[DurationMilliSec] = None
    periodDl: Optional[DurationMilliSec] = None
    qosMonDatRate: Optional[QosMonitoringInformation] = None
    avrgWndw: Optional[AverWindow] = None
    servAuthInfo: Optional[ServAuthInfo] = None
    qosMonConReq: Optional[QosMonitoringInformation] = None
    listUeConsDtRt: Annotated[
        Optional[List[IpAddr]],
        Field(
            description="Identifies the list of UE addresses subject for Consolidated Data Rate monitoring.",
            min_length=1,
        ),
    ] = None


class MultiModalFlows(BaseModel):
    medCompN: Annotated[
        int,
        Field(
            description="It contains the ordinal number of the single-modal data flow. Identifies the single-modal data flow.",
        ),
    ]
    flowIds: Annotated[
        Optional[List[int]],
        Field(
            description="Identifies the affected flow(s) within the single-modal data flow (identified by the medCompN attribute). It may be omitted when all flows are affected.",
            min_length=1,
        ),
    ] = None


class QosMonitoringReport(BaseModel):
    ulDelays: Annotated[Optional[List[Uinteger]], Field(min_length=1)] = None
    dlDelays: Annotated[Optional[List[Uinteger]], Field(min_length=1)] = None
    rtDelays: Annotated[Optional[List[Uinteger]], Field(min_length=1)] = None
    pdmf: Annotated[
        Optional[bool],
        Field(description="Represents the packet delay measurement failure indicator."),
    ] = None
    ulDataRate: Optional[BitRate] = None
    dlDataRate: Optional[BitRate] = None
    ulAggrDataRate: Optional[BitRate] = None
    dlAggrDataRate: Optional[BitRate] = None
    ulConInfo: Optional[Uinteger] = None
    dlConInfo: Optional[Uinteger] = None


class UserPlaneEventReport(BaseModel):
    event: UserPlaneEvent
    accumulatedUsage: Optional[AccumulatedUsage] = None
    flowIds: Annotated[
        Optional[List[int]],
        Field(
            description="Identifies the affected flows that were sent during event subscription. It might be omitted when the reported event applies to all the flows sent during the subscription.",
            min_length=1,
        ),
    ] = None
    multiModFlows: Annotated[
        Optional[List[MultiModalFlows]],
        Field(
            description="Identifies the the flow filters for the single-modal data flows thatwere sent during event subscription. It may be omitted when the reported event applies to all the single-modal data flows sent during the subscription.",
            min_length=1,
        ),
    ] = None
    appliedQosRef: Annotated[
        Optional[str],
        Field(
            description="The currently applied QoS reference. Applicable for event QOS_NOT_GUARANTEED or SUCCESSFUL_RESOURCES_ALLOCATION.",
        ),
    ] = None
    altQosNotSuppInd: Annotated[
        Optional[bool],
        Field(
            description="When present and set to true it indicates that the Alternative QoS profiles are not supported by the access network. Applicable for event QOS_NOT_GUARANTEED.",
        ),
    ] = None
    plmnId: Optional[PlmnIdNid] = None
    qosMonReports: Annotated[
        Optional[List[QosMonitoringReport]],
        Field(
            description="Contains the QoS Monitoring Reporting information",
            min_length=1,
        ),
    ] = None
    pdvMonReports: Annotated[
        Optional[List[PdvMonitoringReport]],
        Field(
            description="Contains the PDV Monitoring Reporting information",
            min_length=1,
        ),
    ] = None
    ratType: Optional[RatType] = None
    batOffsetInfo: Optional[BatOffsetInfo] = None
    rttMonReports: Annotated[
        Optional[List[QosMonitoringReport]],
        Field(
            description="Contains the round trip delay over two SDFs reporting information",
            min_length=1,
        ),
    ] = None
    qosMonDatRateReps: Annotated[
        Optional[List[QosMonitoringReport]],
        Field(
            description='Contains QoS Monitoring for data rate information. It shall be present when the notified event is "QOS_MONITORING" and data rate measurements are available.',
            min_length=1,
        ),
    ] = None
    aggrDataRateRpts: Annotated[
        Optional[List[QosMonitoringReport]],
        Field(
            description='Contains QoS Monitoring for aggregated data rate information. It shall be present when the notified event is "QOS_MONITORING" and data rate measurements are available.',
            min_length=1,
        ),
    ] = None
    qosMonConInfoReps: Annotated[
        Optional[List[QosMonitoringReport]],
        Field(
            description='Contains QoS Monitoring for congestion information. It shall be present when the notified event is "QOS_MONITORING" and congestion measurements are available.\n',
            min_length=1,
        ),
    ] = None


class UserPlaneNotificationData(BaseModel):
    transaction: Link
    eventReports: Annotated[
        List[UserPlaneEventReport],
        Field(
            description="Contains the reported event and applicable information",
            min_length=1,
        ),
    ]
