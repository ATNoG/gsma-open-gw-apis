import enum
from fastapi.encoders import jsonable_encoder
import httpx
import logging
from datetime import datetime
from pydantic import AnyHttpUrl, AnyUrl

from app.drivers.nef_auth import NEFAuth
from app.interfaces.reachability_status import ReachabilityStatusInterface
from app.schemas.device import Device
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringEventSubscription,
    MonitoringType,
    ReachabilityType,
)
from app.schemas.reachability_status import ConnectivityType, ReachabilityStatusResponse


class _ConnectivityStatus(enum.Enum):
    Connected = enum.auto()
    NoConnectivity = enum.auto()
    Unknown = enum.auto()


class NefReachabilityStatusInterface(ReachabilityStatusInterface):
    def __init__(self, nef_url: AnyHttpUrl, nef_auth: NEFAuth) -> None:
        super().__init__()
        self.httpx_client = httpx.AsyncClient(base_url=str(nef_url), auth=nef_auth)

    async def _delete_subscription(self, sub_url: AnyUrl) -> None:
        res = await self.httpx_client.delete(str(sub_url))

        if res.status_code == 404:
            logging.warning("Subscription not found")
            return

        if not res.is_success:
            logging.error(
                "Failed to delete subscription (code: {%d}): %s",
                res.status_code,
                res.text,
            )

    async def _check_connectivity(
        self, device: Device, type: ReachabilityType
    ) -> _ConnectivityStatus:
        data = MonitoringEventSubscription(
            monitoringType=MonitoringType.UE_REACHABILITY,
            notificationDestination=AnyHttpUrl("https://0.0.0.0"),
            maximumNumberOfReports=1,
            addnMonTypes=[MonitoringType.LOSS_OF_CONNECTIVITY],
            reachabilityType=type,
        )

        if device.phoneNumber is not None:
            data.msisdn = device.phoneNumber.lstrip("+")
        elif device.ipv4Address is not None:
            data.ipv4Addr = device.ipv4Address.publicAddress
        elif device.ipv6Address is not None:
            data.ipv6Addr = device.ipv6Address
        elif device.networkAccessIdentifier is not None:
            data.externalId = device.networkAccessIdentifier

        res = await self.httpx_client.post(
            "/nef/api/v1/3gpp-monitoring-event/v1/myNetApp/subscriptions",
            json=jsonable_encoder(data),
        )

        if not res.is_success:
            logging.error("Failed to create NEF subscription")
            raise RuntimeError()

        sub = MonitoringEventSubscription.model_validate(res.json())

        # No report was available so the device doesn't have data but also
        # isn't disconnected.
        if res.status_code == 201:
            assert sub.self is not None
            await self._delete_subscription(sub.self)
            return _ConnectivityStatus.Unknown

        monType = res.json()["monitoringType"]

        if monType == "LOSS_OF_CONNECTIVITY":
            return _ConnectivityStatus.NoConnectivity
        elif monType == "UE_REACHABILITY":
            return _ConnectivityStatus.Connected

        return _ConnectivityStatus.Unknown

    async def get_reachability_status(
        self, device: Device
    ) -> ReachabilityStatusResponse:
        res = ReachabilityStatusResponse(lastStatusTime=datetime.now(), reachable=False)

        data_connectivity = await self._check_connectivity(device, ReachabilityType.SMS)

        if data_connectivity == _ConnectivityStatus.NoConnectivity:
            res.reachable = False
            return res
        elif data_connectivity == _ConnectivityStatus.Connected:
            res.reachable = True
            res.connectivity = [ConnectivityType.DATA]

        sms_connectivity = await self._check_connectivity(device, ReachabilityType.SMS)

        if sms_connectivity == _ConnectivityStatus.NoConnectivity:
            res.reachable = False
            res.connectivity = None
            return res
        elif data_connectivity == _ConnectivityStatus.Connected:
            res.reachable = True
            if res.connectivity is None:
                res.connectivity = []
            res.connectivity.append(ConnectivityType.SMS)

        return res
