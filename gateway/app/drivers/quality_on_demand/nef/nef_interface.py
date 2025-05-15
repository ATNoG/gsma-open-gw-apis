import datetime
import logging
from typing import Awaitable, List
import uuid

import httpx

from app.drivers.nef_auth import NEFAuth
from app.exceptions import (
    InternalServerError,
    ResourceNotFound,
    UnsupportedIdentifier,
)
from app.interfaces.quality_on_demand import (
    QoDInterface,
    SessionConflict,
)
from app.redis import get_redis
from app.schemas.device import Device
from app.schemas.nef_schemas.afSessionWithQos import (
    AsSessionWithQoSSubscription,
    AsSessionWithQoSSubscriptionPatch,
    UserPlaneNotificationData,
)
from app.schemas.nef_schemas.commonData import (
    FlowInfo,
    Link,
    UsageThreshold,
    UserPlaneEvent,
)

from app.schemas.qodProvisioning import (
    Status,
)
from app.schemas.quality_on_demand import (
    BaseSessionInfo,
    CreateSession,
    Data,
    EventQosStatus,
    ExtendSessionDuration,
    PortsSpec,
    SessionInfo,
    NotificationEventType,
    CloudEvent,
    StatusInfo,
)
from app.schemas.subscriptions import Datacontenttype, Specversion
from app.settings import NEFSettings

_prefix_info = "qodinfo"
_prefix_gateway_nef = "qodnef"
_prefix_device = "qodDevice"
LOG = logging.getLogger(__name__)


class NEFQoDInterface(QoDInterface):
    def __init__(self, nef_settings: NEFSettings, source: str) -> None:
        super().__init__()

        nef_auth = NEFAuth(
            nef_settings.url, nef_settings.username, nef_settings.password
        )
        self.httpx_client = httpx.AsyncClient(
            base_url=nef_settings.get_base_url(), auth=nef_auth
        )
        self.httpx_client_callback = httpx.AsyncClient()

        self.af_id = nef_settings.gateway_af_id
        self.source = source
        self.notification_url = nef_settings.get_notification_url()

        self.redis = get_redis()

    async def create_provisioning(
        self, req: CreateSession, device: Device
    ) -> SessionInfo:
        qod_id = uuid.uuid4()

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
            qosStatus=Status.REQUESTED,
        )
        await self._save_subscription_info(str(qod_id), response)

        payload = AsSessionWithQoSSubscription(
            supportedFeatures="800820",
            notificationDestination=Link(
                f"{self.notification_url}/callbacks/v1/qod/{qod_id}"
            ),
            flowInfo=self._get_flow_info(req),
            qosReference=req.qosProfile,
            usageThreshold=UsageThreshold(duration=req.duration),
        )

        if device.ipv4Address and device.ipv4Address.publicAddress:
            payload.ueIpv4Addr = device.ipv4Address.publicAddress
        elif device.ipv6Address:
            payload.ueIpv6Addr = device.ipv6Address
        elif device.phoneNumber:
            phone_number = device.phoneNumber.lstrip("+")
            payload.gpsi = f"msisdn-{phone_number}"

        res = await self.httpx_client.post(
            f"/3gpp-as-session-with-qos/v1/{self.af_id}/subscriptions",
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )

        if res.status_code == 404:
            raise ResourceNotFound()

        if res.status_code == 409:
            raise SessionConflict()

        if not res.is_success:
            raise InternalServerError()

        subcription_result = AsSessionWithQoSSubscription.model_validate_json(
            res.content
        )

        nef_sub_id = str(subcription_result.self)

        key = f"{_prefix_gateway_nef}:{str(qod_id)}"
        await self.redis.set(key, nef_sub_id)

        if device.phoneNumber:
            key = f"{_prefix_device}:{device.phoneNumber}"
            await self._save_device(key, str(qod_id))
        if device.networkAccessIdentifier:
            key = f"{_prefix_device}:{device.networkAccessIdentifier}"
            await self._save_device(key, str(qod_id))
        if device.ipv4Address and device.ipv4Address.privateAddress:
            key = f"{_prefix_device}:{device.ipv4Address.privateAddress}"
            await self._save_device(key, str(qod_id))
        if device.ipv4Address and device.ipv4Address.publicPort:
            key = f"{_prefix_device}:{device.ipv4Address.publicAddress}:{device.ipv4Address.publicPort}"
            await self._save_device(key, str(qod_id))
        if device.ipv6Address:
            key = f"{_prefix_device}:{device.ipv6Address.exploded}"
            await self._save_device(key, str(qod_id))

        return response

    async def get_qod_information_by_id(self, id: str) -> SessionInfo:
        key = f"{_prefix_info}:{id}"

        data = await self.redis.get(key)

        return SessionInfo.model_validate_json(data)

    async def delete_qod_session(self, id: str) -> SessionInfo:
        sub_info = await self.get_qod_information_by_id(id)

        if sub_info.qosStatus == Status.UNAVAILABLE:
            return sub_info

        key = f"{_prefix_gateway_nef}:{id}"
        nef_id = await self.redis.get(key)

        res = await self.httpx_client.delete(nef_id)

        if res.status_code == 404:
            raise ResourceNotFound()

        if not res.is_success:
            raise InternalServerError()

        if res.status_code == 204:
            sub_info.qosStatus = Status.UNAVAILABLE
            sub_info.statusInfo = StatusInfo.DELETE_REQUESTED

        await self._save_subscription_info(id, sub_info)

        return sub_info

    async def get_qod_information_device(self, device: Device) -> List[SessionInfo]:
        id = []

        if device.phoneNumber:
            key = f"{_prefix_device}:{device.phoneNumber}"
            id = await self._get_device(key)
        elif device.networkAccessIdentifier:
            key = f"{_prefix_device}:{device.networkAccessIdentifier}"
            id = await self._get_device(key)
        elif device.ipv4Address and device.ipv4Address.privateAddress:
            key = f"{_prefix_device}:{device.ipv4Address.privateAddress}"
            id = await self._get_device(key)
        elif device.ipv4Address and device.ipv4Address.publicPort:
            key = f"{_prefix_device}:{device.ipv4Address.publicAddress}:{device.ipv4Address.publicPort}"
            id = await self._get_device(key)
        elif device.ipv6Address:
            key = f"{_prefix_device}:{device.ipv6Address.exploded}"
            id = await self._get_device(key)

        if len(id) == 0 or id is None:
            raise ResourceNotFound()

        sub_info = []

        for sub_id in id:
            sub_info.append(await self.get_qod_information_by_id(sub_id))

        return sub_info

    async def extend_session(self, id: str, req: ExtendSessionDuration) -> SessionInfo:
        sub_info = await self.get_qod_information_by_id(id)

        if sub_info.qosStatus == Status.UNAVAILABLE:
            return sub_info

        if sub_info.device is None:
            raise ResourceNotFound()

        if sub_info.expiresAt is None:
            sub_info.expiresAt = datetime.datetime.now() + datetime.timedelta(
                seconds=req.requestedAdditionalDuration
            )
        else:
            sub_info.expiresAt = sub_info.expiresAt + datetime.timedelta(
                seconds=req.requestedAdditionalDuration
            )

        sub_info.duration = sub_info.duration + req.requestedAdditionalDuration

        await self._save_subscription_info(id, sub_info)

        key = f"{_prefix_gateway_nef}:{id}"
        nef_id = await self.redis.get(key)

        payload = AsSessionWithQoSSubscriptionPatch(
            usageThreshold=UsageThreshold(
                duration=sub_info.duration,
            ),
        )

        res = await self.httpx_client.patch(
            nef_id,
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )

        if res.status_code == 404:
            raise ResourceNotFound()

        if not res.is_success:
            raise InternalServerError()

        return sub_info

    async def send_callback_message(
        self, body: UserPlaneNotificationData, id: str
    ) -> None:
        sub_info = await self.get_qod_information_by_id(id)

        if sub_info is None:
            raise ResourceNotFound()

        status = self._get_qod_status(body)
        if status is not None:
            sub_info.qosStatus = status

        if sub_info.qosStatus == Status.UNAVAILABLE:
            sub_info.statusInfo = StatusInfo.NETWORK_TERMINATED

        sink = sub_info.sink
        if sink is None:
            return

        cloud_event = CloudEvent(
            id=str(uuid.uuid4()),
            source=self.source,
            type=NotificationEventType.org_camaraproject_quality_on_demand_v1_qos_status_changed,
            specversion=Specversion.field_1_0,
            datacontenttype=Datacontenttype.application_json,
            data=Data(
                sessionId=sub_info.sessionId,
                qosStatus=EventQosStatus.AVAILABLE
                if sub_info.qosStatus == Status.AVAILABLE
                else EventQosStatus.UNAVAILABLE,
                statusInfo=sub_info.statusInfo,
            ),
            time=datetime.datetime.now(),
        )

        await self.httpx_client_callback.post(
            str(sink),
            content=cloud_event.model_dump_json(exclude_unset=True, by_alias=True),
        )

        await self._save_subscription_info(id, sub_info)

    def _get_qod_status(self, nef_response: UserPlaneNotificationData) -> Status | None:
        status = None
        for report in nef_response.eventReports:
            if report.event == UserPlaneEvent.QOS_GUARANTEED:
                status = Status.AVAILABLE
            elif report.event == UserPlaneEvent.FAILED_RESOURCES_ALLOCATION:
                status = Status.UNAVAILABLE
            elif report.event == UserPlaneEvent.QOS_NOT_GUARANTEED:
                status = Status.REQUESTED
            elif report.event == UserPlaneEvent.SUCCESSFUL_RESOURCES_ALLOCATION:
                status = Status.AVAILABLE
        return status

    async def _save_subscription_info(self, id: str, data: SessionInfo) -> None:
        key = f"{_prefix_info}:{id}"

        await self.redis.set(
            key, data.model_dump_json(exclude_unset=True, by_alias=True)
        )

    def _get_flow_info(self, req: BaseSessionInfo) -> List[FlowInfo]:
        flow = []

        device_ports = ""
        if req.devicePorts:
            device_ports = self._format_ports(req.devicePorts)

        server_ports = ""
        if req.applicationServerPorts:
            server_ports = self._format_ports(req.applicationServerPorts)

        dev_to_app_ips = []

        if (
            req.device
            and req.device.ipv4Address is not None
            and req.applicationServer.ipv4Address is not None
        ):
            dev_to_app_ips.append(
                (
                    str(req.device.ipv4Address.publicAddress),
                    req.applicationServer.ipv4Address,
                )
            )

        if (
            req.device
            and req.device.ipv6Address
            and req.applicationServer.ipv6Address is not None
        ):
            dev_to_app_ips.append(
                (str(req.device.ipv6Address), req.applicationServer.ipv6Address)
            )

        if len(dev_to_app_ips) == 0:
            raise UnsupportedIdentifier()

        for i, (dev_ip, app_ip) in enumerate(dev_to_app_ips):
            src_to_dst = f"permit in ip from {dev_ip}"
            if device_ports != "":
                src_to_dst += f" {device_ports}"
            src_to_dst += f" to {app_ip}"
            if server_ports != "":
                src_to_dst += f" {server_ports}"

            dst_to_src = f"permit out ip from {app_ip}"
            if server_ports != "":
                dst_to_src += f" {server_ports}"
            dst_to_src += f" to {dev_ip}"
            if device_ports != "":
                dst_to_src += f" {device_ports}"

            flow.append(
                FlowInfo(
                    flowId=i,
                    flowDescriptions=[src_to_dst, dst_to_src],
                )
            )

        return flow

    def _format_ports(self, port_specs: PortsSpec) -> str:
        ports = ""

        if port_specs.ports:
            ports = str(port_specs.ports[0])
            for port in port_specs.ports[1:]:
                ports += f",{port}"
        if port_specs.ranges:
            if ports:
                ports += ","
            ports += f"{port_specs.ranges[0].from_}-{port_specs.ranges[0].to}"
            for ranges in port_specs.ranges[1:]:
                ports += f",{ranges.from_}-{ranges.to}"
        return ports

    async def _save_device(self, key: str, id: str) -> None:
        res = self.redis.rpush(key, id)
        if isinstance(res, Awaitable):
            res = await res

    async def _get_device(self, key: str) -> List[str]:
        res = self.redis.lrange(key, 0, -1)
        if isinstance(res, Awaitable):
            res = await res

        return res
