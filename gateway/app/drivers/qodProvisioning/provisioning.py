import datetime
import logging
import uuid

import httpx
from pydantic import AnyUrl

from app.interfaces.qodProvisioning import (
    QoDProvisioningAbstractInterface,
    ResourceNotFound,
)
from app.redis import get_redis
from app.schemas.afSessionWithQos import AsSessionWithQoSSubscription
from app.schemas.commonData import (
    FlowInfo,
    Gpsi,
    SupportedFeatures,
    UserPlaneEvent1,
    UserPlaneNotificationData,
)
from app.schemas.qodProvisioning import (
    CloudEvent,
    CreateProvisioning,
    ProvisioningId,
    ProvisioningInfo,
    RetrieveProvisioningByDevice,
    Status,
)
from app.settings import settings

_prefix_info = "qodprovisioninginfo"
_prefix_gateway_nef = "qodprovisioningnef"
LOG = logging.getLogger(__name__)


class RedisQoDProvisioningInterface(QoDProvisioningAbstractInterface):
    def __init__(self) -> None:
        super().__init__()
        self.httpx_client = httpx.AsyncClient()
        self.redis = get_redis()

    async def crate_provisioning(self, req: CreateProvisioning) -> ProvisioningInfo:
        provisioning_id = uuid.uuid4()

        payload = AsSessionWithQoSSubscription(
            supportedFeatures=SupportedFeatures(__root__=""),
            notificationDestination=f"{settings.provisioning.gateway_url}/{provisioning_id}",
            flowInfo=[
                FlowInfo(
                    flowId=0,
                    flowDescriptions=[
                        "permit in ip any to any",
                        "permit out ip any to any",
                    ],
                )
            ],
            qosReference=req.qosProfile.__root__,
            ueIpv4Addr=req.device.ipv4Address.__root__.publicAddress.__root__,
            ueIpv6Addr=req.device.ipv6Address.__root__,
            gpsi=Gpsi(__root__=f"msisdn-{req.device.phoneNumber}"),
        )

        res = await self.httpx_client.post(
            f"{settings.provisioning.nef_url}/{settings.provisioning.as_id}/subcriptions",
            content=payload.model_dump_json(),
        )

        if res.status_code != 404:
            raise ResourceNotFound()

        subcription_result = AsSessionWithQoSSubscription.model_validate_json(
            res.content
        )

        # TODO: Make sure this a UUID
        nef_sub_id = self._get_subscription_id_from_subscription_url(
            subcription_result.self
        )

        response = ProvisioningInfo(
            device=req.device,
            qosProfile=req.qosProfile,
            status=Status.REQUESTED,
            sink=req.sink,
            provisioningId=ProvisioningId(__root__=provisioning_id),
            startedAt=datetime.datetime.now(),
        )

        key = f"{_prefix_info}:{id}"
        self.redis.set(key, response.model_dump_json())

        key = f"{_prefix_gateway_nef}:{id}"
        self.redis.set(key, nef_sub_id)

        return response

    async def get_qod_information_by_id(self, id: str) -> ProvisioningInfo:

    async def delete_qod_provisioning(self, id: str) -> ProvisioningInfo:
        raise NotImplementedError

    async def get_qod_information_device(
        self, device: RetrieveProvisioningByDevice
    ) -> ProvisioningInfo:
        raise NotImplementedError

    async def send_callback_message(
        self, body: UserPlaneNotificationData, id: str
    ) -> None:
        key = f"{_prefix_info}:{id}"
        sub_info = ProvisioningInfo.model_validate_json(await self.redis.get(key))

        if sub_info is None:
            raise ResourceNotFound()

        #TODO: change this to cloud event
        cloud_event = CloudEvent(id=uuid.uuid4(), source=)

        sink = sub_info.sink

        if sink is None:
            raise Exception()

        await self.httpx_client.post(sink, content=sub_info.model_dump_json())

    def _get_subscription_id_from_subscription_url(self, url: AnyUrl | None) -> str:
        if url is None or url.path is None:
            raise Exception("Invalid url")

        return url.path.rsplit("/")[-1]
