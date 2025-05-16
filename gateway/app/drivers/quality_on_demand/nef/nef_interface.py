import datetime
import logging
from typing import List
import uuid

import httpx
from pydantic import AnyHttpUrl

from app.drivers.nef_auth import NEFAuth
from app.exceptions import BadRequest, ResourceNotFound, UnsupportedIdentifier
from app.interfaces.quality_on_demand import (
    QoDInterface,
    SessionConflict,
)
from app.redis import get_redis
from app.schemas.device import Device
from app.schemas.nef_schemas.afSessionWithQos import (
    AsSessionWithQoSSubscription,
    UserPlaneNotificationData,
)
from app.schemas.nef_schemas.commonData import (
    FlowInfo,
    Link,
    UsageThreshold,
    UserPlaneEvent,
)

from app.schemas.quality_on_demand import (
    CreateSession,
    Datacontenttype,
    ExtendSessionDuration,
    QosStatus,
    SessionInfo,
    CloudEvent,
    Specversion,
    StatusInfo,
    Type,
)
from app.settings import settings

_prefix_info = "qodinfo"
_prefix_gateway_nef = "qodnef"
_prefix_device = "qodDevice"
LOG = logging.getLogger(__name__)


class NEFQoDInterface(QoDInterface):
    def __init__(self, nef_url: AnyHttpUrl, nef_auth: NEFAuth) -> None:
        super().__init__()
        self.httpx_client = httpx.AsyncClient(base_url=str(nef_url), auth=nef_auth)
        self.httpx_client_callback = httpx.AsyncClient()
        self.redis = get_redis()

    async def create_provisioning(
        self, req: CreateSession, device: Device
    ) -> SessionInfo:
        qod_id = uuid.uuid4()

        payload = AsSessionWithQoSSubscription(
            supportedFeatures="0",
            notificationDestination=Link(
                f"{settings.nef_gateway_url}callbacks/v1/qod/{qod_id}"
            ),
            flowInfo=[
                FlowInfo(
                    flowId=0,
                    flowDescriptions=self._get_flow_description(req),
                )
            ],
            qosReference=req.qosProfile,
            usageThreshold=UsageThreshold(
                duration=req.duration, totalVolume=0, downlinkVolume=0, uplinkVolume=0
            ),
        )

        if device.ipv4Address and device.ipv4Address.publicAddress:
            payload.ueIpv4Addr = device.ipv4Address.publicAddress
        elif device.ipv6Address:
            payload.ueIpv6Addr = device.ipv6Address
        elif device.phoneNumber:
            phone_number = device.phoneNumber.lstrip("+")
            payload.gpsi = f"msisdn-{phone_number}"

        res = await self.httpx_client.post(
            f"/nef/api/v1/3gpp-as-session-with-qos/v1/{settings.qod_provisioning.af_id}/subscriptions",
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )

        if res.status_code == 404:
            raise ResourceNotFound()

        if res.status_code == 409:
            raise SessionConflict()

        if not res.is_success:
            raise BadRequest()

        subcription_result = AsSessionWithQoSSubscription.model_validate_json(
            res.content
        )

        nef_sub_id = str(subcription_result.self)

        response = SessionInfo(
            sessionId=qod_id,
            device=device,
            applicationServer=req.applicationServer,
            devicePorts=req.devicePorts,
            applicationServerPorts=req.applicationServerPorts,
            qosProfile=req.qosProfile,
            duration=req.duration,
            sink=req.sink,
            startedAt=datetime.datetime.now(),
            expiresAt=datetime.datetime.now()
            + datetime.timedelta(seconds=req.duration),
            qosStatus=QosStatus.REQUESTED,
        )
        await self._save_subscription_info(str(qod_id), response)

        key = f"{_prefix_gateway_nef}:{str(qod_id)}"
        await self.redis.set(key, nef_sub_id)

        if device.phoneNumber:
            key = f"{_prefix_device}:{device.phoneNumber}"
            await self.redis.set(key, str(qod_id))
        if device.networkAccessIdentifier:
            key = f"{_prefix_device}:{device.networkAccessIdentifier}"
            await self.redis.set(key, str(qod_id))
        if device.ipv4Address and device.ipv4Address.privateAddress:
            key = f"{_prefix_device}:{device.ipv4Address.privateAddress}"
            await self.redis.set(key, str(qod_id))
        if device.ipv4Address and device.ipv4Address.publicPort:
            key = f"{_prefix_device}:{device.ipv4Address.publicAddress}:{device.ipv4Address.publicPort}"
            await self.redis.set(key, str(qod_id))
        if device.ipv6Address:
            key = f"{_prefix_device}:{device.ipv6Address.exploded}"
            await self.redis.set(key, str(qod_id))

        return response

    async def get_qod_information_by_id(self, id: str) -> SessionInfo:
        key = f"{_prefix_info}:{id}"

        data = await self.redis.get(key)

        return SessionInfo.model_validate_json(data)

    async def delete_qod_session(self, id: str) -> SessionInfo:
        key = f"{_prefix_gateway_nef}:{id}"
        nef_id = await self.redis.get(key)

        sub_info = await self.get_qod_information_by_id(id)

        if sub_info.statusInfo == StatusInfo.DELETE_REQUESTED:
            return sub_info

        res = await self.httpx_client.delete(nef_id)

        if res.status_code == 404:
            raise ResourceNotFound()

        if not res.is_success:
            raise BadRequest()

        if res.status_code == 204:
            sub_info.qosStatus = QosStatus.UNAVAILABLE
            sub_info.statusInfo = StatusInfo.DELETE_REQUESTED

        await self._save_subscription_info(id, sub_info)

        return sub_info

    async def get_qod_information_device(self, device: Device) -> SessionInfo:
        id = ""

        if device.phoneNumber:
            key = f"{_prefix_device}:{device.phoneNumber}"
            id = await self.redis.get(key)
        elif device.networkAccessIdentifier:
            key = f"{_prefix_device}:{device.networkAccessIdentifier}"
            id = await self.redis.get(key)
        elif device.ipv4Address and device.ipv4Address.privateAddress:
            key = f"{_prefix_device}:{device.ipv4Address.privateAddress}"
            id = await self.redis.get(key)
        elif device.ipv4Address and device.ipv4Address.publicPort:
            key = f"{_prefix_device}:{device.ipv4Address.publicAddress}:{device.ipv4Address.publicPort}"
            id = await self.redis.get(key)
        elif device.ipv6Address:
            key = f"{_prefix_device}:{device.ipv6Address.exploded}"
            id = await self.redis.get(key)

        if id == "" or id is None:
            raise ResourceNotFound()

        sub_info = await self.get_qod_information_by_id(id)

        return sub_info

    async def extend_session(self, id: str, req: ExtendSessionDuration) -> SessionInfo:
        sub_info = await self.get_qod_information_by_id(id)

        if sub_info.device is None:
            raise ResourceNotFound()

        key = f"{_prefix_gateway_nef}:{id}"
        nef_id = await self.redis.get(key)

        payload = AsSessionWithQoSSubscription(
            self=nef_id,
            supportedFeatures="0",
            notificationDestination=Link(
                f"{settings.nef_gateway_url}callbacks/v1/qod/{id}"
            ),
            flowInfo=[
                FlowInfo(
                    flowId=0,
                    flowDescriptions=self._get_flow_description(sub_info),
                )
            ],
            qosReference=sub_info.qosProfile,
            usageThreshold=UsageThreshold(
                duration=sub_info.duration + req.requestedAdditionalDuration,
                totalVolume=0,
                downlinkVolume=0,
                uplinkVolume=0,
            ),
        )

        if sub_info.device.ipv4Address and sub_info.device.ipv4Address.publicAddress:
            payload.ueIpv4Addr = sub_info.device.ipv4Address.publicAddress
        elif sub_info.device.ipv6Address:
            payload.ueIpv6Addr = sub_info.device.ipv6Address
        elif sub_info.device.phoneNumber:
            phone_number = sub_info.device.phoneNumber.lstrip("+")
            payload.gpsi = f"msisdn-{phone_number}"

        res = await self.httpx_client.put(
            nef_id,
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )

        if res.status_code == 404:
            raise ResourceNotFound()

        if not res.is_success:
            raise BadRequest()

        if sub_info.expiresAt is None:
            raise ResourceNotFound()

        response = SessionInfo(
            sessionId=sub_info.sessionId,
            device=sub_info.device,
            applicationServer=sub_info.applicationServer,
            devicePorts=sub_info.devicePorts,
            applicationServerPorts=sub_info.applicationServerPorts,
            qosProfile=sub_info.qosProfile,
            duration=sub_info.duration + req.requestedAdditionalDuration,
            startedAt=sub_info.startedAt,
            expiresAt=sub_info.expiresAt
            + datetime.timedelta(seconds=req.requestedAdditionalDuration),
            qosStatus=QosStatus.REQUESTED,
        )
        await self._save_subscription_info(id, response)

        return response

    async def send_callback_message(
        self, body: UserPlaneNotificationData, id: str
    ) -> None:
        sub_info = await self.get_qod_information_by_id(id)

        if sub_info is None:
            raise ResourceNotFound()

        status = self._get_qod_status(body)
        if status is not None:
            sub_info.qosStatus = status

        if sub_info.qosStatus == QosStatus.UNAVAILABLE:
            sub_info.statusInfo = (
                StatusInfo.NETWORK_TERMINATED
                if sub_info.qosStatus == QosStatus.UNAVAILABLE
                and sub_info.statusInfo != StatusInfo.DELETE_REQUESTED
                else sub_info.statusInfo
            )

        cloud_event = CloudEvent(
            id=str(uuid.uuid4()),
            source=f"{settings.gateway_url}qod-provisioning/v0.2/device-qos/{id}",
            type=Type.org_camaraproject_quality_on_demand_v1_qos_status_changed,
            specversion=Specversion.field_1_0,
            datacontenttype=Datacontenttype.application_json,
            data=sub_info.model_dump(mode="json", exclude_unset=True),
            time=datetime.datetime.now(),
        )

        sink = sub_info.sink
        if sink is None:
            raise ResourceNotFound()

        await self.httpx_client_callback.post(
            str(sink),
            content=cloud_event.model_dump_json(exclude_unset=True, by_alias=True),
        )

        await self._save_subscription_info(id, sub_info)

    def _get_qod_status(
        self, nef_response: UserPlaneNotificationData
    ) -> QosStatus | None:
        status = None
        for report in nef_response.eventReports:
            if report.event == UserPlaneEvent.QOS_GUARANTEED:
                status = QosStatus.AVAILABLE
            elif report.event == UserPlaneEvent.FAILED_RESOURCES_ALLOCATION:
                status = QosStatus.UNAVAILABLE
            elif report.event == UserPlaneEvent.QOS_NOT_GUARANTEED:
                status = QosStatus.REQUESTED
            elif report.event == UserPlaneEvent.SUCCESSFUL_RESOURCES_ALLOCATION:
                status = QosStatus.AVAILABLE
        return status

    async def _save_subscription_info(self, id: str, data: SessionInfo) -> None:
        key = f"{_prefix_info}:{id}"

        await self.redis.set(
            key, data.model_dump_json(exclude_unset=True, by_alias=True)
        )

    def _get_flow_description(self, req: CreateSession | SessionInfo) -> List[str]:
        flow_description = []
        if req.applicationServerPorts is None or req.devicePorts is None:
            raise ResourceNotFound()

        if req.applicationServerPorts.ports is None or req.devicePorts.ports is None:
            raise ResourceNotFound()

        if req.device and req.device.ipv4Address is not None:
            flow_description.append(
                f"permit in ip from {req.device.ipv4Address.publicAddress} {req.devicePorts.ports[0]} to {req.applicationServer.ipv4Address} {req.applicationServerPorts.ports[0]}"
            )
            flow_description.append(
                f"permit in ip from {req.applicationServer.ipv4Address} {req.applicationServerPorts.ports[0]} to {req.device.ipv4Address.publicAddress} {req.devicePorts.ports[0]}"
            )

        elif req.device and req.device.ipv6Address:
            flow_description.append(
                f"permit in ip from {req.device.ipv6Address.exploded} to {req.applicationServer.ipv6Address}"
            )
            flow_description.append(
                f"permit in ip from {req.applicationServer.ipv6Address} to {req.device.ipv6Address.exploded}"
            )

        else:
            raise UnsupportedIdentifier()
        return flow_description
