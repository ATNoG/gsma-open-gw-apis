import datetime
import logging
import uuid

import httpx

from app.exceptions import ResourceNotFound
from app.drivers.nef_auth import NEFAuth
from app.interfaces.qodProvisioning import (
    ProvisioningConflict,
    QoDProvisioningInterface,
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
    UserPlaneEvent,
)
from app.schemas.subscriptions import (
    Datacontenttype,
    Specversion,
)
from app.schemas.qodProvisioning import (
    CloudEvent,
    CloudEventData,
    NotificationEventType,
    StatusChanged,
    TriggerProvisioning,
    ProvisioningInfo,
    Status,
    StatusInfo,
)
from app.settings import NEFSettings

_prefix_info = "qodprovisioninginfo"
_prefix_gateway_nef = "qodprovisioningnef"
_prefix_device = "qodDevice"
LOG = logging.getLogger(__name__)


class NEFQoDProvisioningInterface(QoDProvisioningInterface):
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
        self, req: TriggerProvisioning, device: Device
    ) -> ProvisioningInfo:
        provisioning_id = uuid.uuid4()

        payload = AsSessionWithQoSSubscription(
            supportedFeatures="800820",
            notificationDestination=Link(
                f"{self.notification_url}/callbacks/v1/qos/{provisioning_id}"
            ),
            flowInfo=[
                FlowInfo(
                    flowId=0,
                    flowDescriptions=[
                        "permit in ip any to any",
                        "permit out ip any to any",
                    ],
                )
            ],
            qosReference=req.qosProfile,
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
            raise ProvisioningConflict()

        subcription_result = AsSessionWithQoSSubscription.model_validate_json(
            res.content
        )

        nef_sub_id = str(subcription_result.self)

        response = ProvisioningInfo(
            device=device,
            qosProfile=req.qosProfile,
            status=Status.REQUESTED,
            sink=req.sink,
            provisioningId=provisioning_id,
            startedAt=datetime.datetime.now(),
        )

        await self._save_subscription_info(str(provisioning_id), response)

        key = f"{_prefix_gateway_nef}:{str(provisioning_id)}"
        await self.redis.set(key, nef_sub_id)

        if device.phoneNumber:
            key = f"{_prefix_device}:{device.phoneNumber}"
            await self.redis.set(key, str(provisioning_id))
        if device.networkAccessIdentifier:
            key = f"{_prefix_device}:{device.networkAccessIdentifier}"
            await self.redis.set(key, str(provisioning_id))
        if device.ipv4Address and device.ipv4Address.privateAddress:
            key = f"{_prefix_device}:{device.ipv4Address.privateAddress}"
            await self.redis.set(key, str(provisioning_id))
        if device.ipv4Address and device.ipv4Address.publicPort:
            key = f"{_prefix_device}:{device.ipv4Address.publicAddress}:{device.ipv4Address.publicPort}"
            await self.redis.set(key, str(provisioning_id))
        if device.ipv6Address:
            key = f"{_prefix_device}:{device.ipv6Address.exploded}"
            await self.redis.set(key, str(provisioning_id))

        return response

    async def get_qod_information_by_id(self, id: str) -> ProvisioningInfo:
        key = f"{_prefix_info}:{id}"

        data = await self.redis.get(key)

        return ProvisioningInfo.model_validate_json(data)

    async def delete_qod_provisioning(self, id: str) -> ProvisioningInfo:
        key = f"{_prefix_gateway_nef}:{id}"
        nef_id = await self.redis.get(key)

        sub_info = await self.get_qod_information_by_id(id)

        if sub_info.statusInfo == StatusInfo.DELETE_REQUESTED:
            return sub_info

        res = await self.httpx_client.delete(nef_id)

        if res.status_code == 404:
            raise ResourceNotFound()

        if res.status_code == 204:
            sub_info.status = Status.UNAVAILABLE
            sub_info.statusInfo = StatusInfo.DELETE_REQUESTED

        await self._save_subscription_info(id, sub_info)

        return sub_info

    async def get_qod_information_device(self, device: Device) -> ProvisioningInfo:
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

    async def send_callback_message(
        self, body: UserPlaneNotificationData, id: str
    ) -> None:
        sub_info = await self.get_qod_information_by_id(id)

        if sub_info is None:
            raise ResourceNotFound()

        status = self._get_qod_status(body)
        if status is not None:
            sub_info.status = status

        if sub_info.status == Status.UNAVAILABLE:
            sub_info.statusInfo = (
                StatusInfo.NETWORK_TERMINATED
                if sub_info.status == Status.UNAVAILABLE
                and sub_info.statusInfo != StatusInfo.DELETE_REQUESTED
                else sub_info.statusInfo
            )

        cloud_event = CloudEvent(
            id=str(uuid.uuid4()),
            source=self.source,
            type=NotificationEventType.org_camaraproject_qod_provisioning_v0_status_changed,
            specversion=Specversion.field_1_0,
            datacontenttype=Datacontenttype.application_json,
            data=CloudEventData(
                provisioningId=sub_info.provisioningId,
                status=StatusChanged.AVAILABLE
                if sub_info.status == Status.AVAILABLE
                else StatusChanged.UNAVAILABLE,
            ),
            time=datetime.datetime.now(),
        )

        sink = sub_info.sink
        if sink is None:
            raise ResourceNotFound()

        await self.httpx_client_callback.post(
            str(sink), content=cloud_event.model_dump_json(exclude_unset=True)
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

    async def _save_subscription_info(self, id: str, data: ProvisioningInfo) -> None:
        key = f"{_prefix_info}:{id}"

        await self.redis.set(key, data.model_dump_json(exclude_unset=True))
