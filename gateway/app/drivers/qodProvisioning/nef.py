import datetime
import logging
from typing import Awaitable
import uuid

import httpx
from pydantic import AnyUrl

from app.interfaces.qodProvisioning import (
    QoDProvisioningInterface,
    ResourceNotFound,
)
from app.redis import get_redis
from app.schemas.afSessionWithQos import (
    AsSessionWithQoSSubscription,
    UserPlaneNotificationData,
)
from app.schemas.commonData import (
    FlowInfo,
    Link,
    UserPlaneEvent,
)
from app.schemas.qodProvisioning import (
    CloudEvent,
    CreateProvisioning,
    Datacontenttype,
    ProvisioningInfo,
    RetrieveProvisioningByDevice,
    Specversion,
    Status,
    StatusInfo,
    Type,
)
from app.settings import settings
import hashlib
import json
from pydantic.json import pydantic_encoder

_prefix_info = "qodprovisioninginfo"
_prefix_gateway_nef = "qodprovisioningnef"
_prefix_device = "qodDevice"
LOG = logging.getLogger(__name__)


class NEFQoDProvisioningInterface(QoDProvisioningInterface):
    def __init__(self) -> None:
        super().__init__()
        self.httpx_client = httpx.AsyncClient()
        self.redis = get_redis()

    async def create_provisioning(self, req: CreateProvisioning) -> ProvisioningInfo:
        provisioning_id = uuid.uuid4()

        payload = AsSessionWithQoSSubscription(
            supportedFeatures="800820",
            notificationDestination=Link(
                f"{settings.gateway_url}/callbacks/v1/qos/{provisioning_id}"
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

        if req.device:
            payload.ueIpv4Addr = req.device.ipv4Address.publicAddress
            payload.ueIpv6Addr = req.device.ipv6Address
            payload.gpsi = (
                f"msisdn-{req.device.phoneNumber}" if req.device.phoneNumber else None
            )

        res = await self.httpx_client.post(
            f"{settings.nef_url}/nef/api/3gpp-as-session-with-qos/v1/{settings.qod_provisioning.af_id}/subcriptions",
            content=payload.model_dump_json(),
        )

        if res.status_code == 404:
            raise ResourceNotFound()

        subcription_result = AsSessionWithQoSSubscription.model_validate_json(
            res.content
        )

        nef_sub_id = self._get_subscription_id_from_subscription_url(
            subcription_result.self
        )

        response = ProvisioningInfo(
            device=req.device,
            qosProfile=req.qosProfile,
            status=Status.REQUESTED,
            sink=req.sink,
            provisioningId=provisioning_id,
            startedAt=datetime.datetime.now(),
        )

        self._save_subscription_info(str(provisioning_id), response)

        key = f"{_prefix_gateway_nef}:{str(provisioning_id)}"
        self.redis.set(key, nef_sub_id)

        # TODO: change this to save every identifier
        if req.device:
            device_hash = hashlib.sha256(
                req.device.model_dump_json().encode("UTF-8")
            ).hexdigest()

            key = f"{_prefix_device}:{device_hash}"
            self.redis.set(key, str(provisioning_id))

        return response

    async def get_qod_information_by_id(self, id: str) -> ProvisioningInfo:
        sub_info = await self._get_subscription_info(id)

        return sub_info

    async def delete_qod_provisioning(self, id: str) -> ProvisioningInfo:
        key = f"{_prefix_gateway_nef}:{id}"
        nef_id = await self.redis.get(key)

        res = await self.httpx_client.delete(
            f"{settings.nef_url}/nef/api/3gpp-as-session-with-qos/v1/{settings.qod_provisioning.af_id}/subcriptions/{nef_id}",
        )

        if res.status_code == 404:
            raise ResourceNotFound()

        sub_info = await self._get_subscription_info(id)

        if res.status_code == 204:
            sub_info.status = Status.UNAVAILABLE
            sub_info.statusInfo = StatusInfo.NETWORK_TERMINATED

        self._save_subscription_info(id, sub_info)

        return sub_info

    async def get_qod_information_device(
        self, device_req: RetrieveProvisioningByDevice
    ) -> ProvisioningInfo:
        if device_req.device is None:
            raise ResourceNotFound()

        device_hash = hashlib.sha256(
            device_req.device.model_dump_json().encode("UTF-8")
        ).hexdigest()

        key = f"{_prefix_device}:{device_hash}"
        id = await self.redis.get(key)

        sub_info = await self._get_subscription_info(id)

        return sub_info

    async def send_callback_message(
        self, body: UserPlaneNotificationData, id: str
    ) -> None:
        sub_info = await self._get_subscription_info(id)

        if sub_info is None:
            raise ResourceNotFound()

        sub_info.status = self._get_qod_status(body)
        sub_info.statusInfo = (
            StatusInfo.NETWORK_TERMINATED
            if sub_info.status == Status.UNAVAILABLE
            else None
        )

        cloud_event = CloudEvent(
            id=str(uuid.uuid4()),
            source=f"{settings.gateway_url}/qod-provisioning/v0.1/device-qos/{id}",
            type=Type.org_camaraproject_qod_provisioning_v0_status_changed,
            specversion=Specversion.field_1_0,
            datacontenttype=Datacontenttype.application_json,
            data=sub_info.model_dump(mode="json"),
            time=datetime.datetime.now(),
        )

        sink = sub_info.sink
        if sink is None:
            raise ResourceNotFound()

        await self.httpx_client.post(sink, content=cloud_event.model_dump_json())

        self._save_subscription_info(id, sub_info)

    def _get_subscription_id_from_subscription_url(self, url: AnyUrl | None) -> str:
        if url is None or url.path is None:
            raise Exception("Invalid url")

        return url.path.rsplit("/", maxsplit=1)[-1]

    def _get_phone_number(self, gpsi: str | None) -> str | None:
        if gpsi is None:
            return None

        phone_number = gpsi.strip("msisdn-")
        return phone_number

    def _get_qod_status(self, nef_response: UserPlaneNotificationData) -> Status:
        if nef_response.eventReports[0].event == UserPlaneEvent.QOS_GUARANTEED:
            return Status.AVAILABLE
        elif nef_response.eventReports[0].event == UserPlaneEvent.SESSION_TERMINATION:
            return Status.UNAVAILABLE
        elif nef_response.eventReports[0].event == UserPlaneEvent.QOS_MONITORING:
            return Status.REQUESTED
        raise Exception

    async def _get_subscription_info(self, id: str) -> ProvisioningInfo:
        key = f"{_prefix_info}:{id}"

        data = self.redis.hgetall(key)
        if isinstance(data, Awaitable):
            data = await data

        decoded_data = {k.decode(): json.loads(v) for k, v in data.items()}

        sub_info = ProvisioningInfo.model_validate(decoded_data)

        return sub_info

    def _save_subscription_info(self, id: str, data: ProvisioningInfo) -> None:
        key = f"{_prefix_info}:{id}"
        data_dict = {
            k: json.dumps(v, default=pydantic_encoder)
            for k, v in data.model_dump().items()
        }

        self.redis.hset(key, mapping=data_dict)
