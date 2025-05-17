import asyncio
import logging
from datetime import datetime

from pydantic import AnyHttpUrl
from fastapi.encoders import jsonable_encoder

from app.interfaces.roaming_status import RoamingStatusInterface
from app.schemas.roaming_status import RoamingStatusResponse
from app.settings import NEFSettings
from app.schemas.device import Device
from app.schemas.nef_schemas.monitoringevent import (
    MonitoringEventReport,
    MonitoringEventSubscription,
    MonitoringType,
)
from app.utils.nef_driver_base import NefDriverBase


class NefRoamingStatusInterface(RoamingStatusInterface, NefDriverBase):
    def __init__(self, nef_settings: NEFSettings) -> None:
        super().__init__(nef_settings)

    async def get_roaming_status(self, device: Device) -> RoamingStatusResponse:
        sub = MonitoringEventSubscription(
            monitoringType=MonitoringType.ROAMING_STATUS,
            notificationDestination=AnyHttpUrl("https://0.0.0.0"),
            maximumNumberOfReports=1,
            plmnIndication=True,
        )

        sub = self.install_device_identifiers(sub, device)

        nef_res = await self.httpx_client.post(
            f"3gpp-monitoring-event/v1/{self.af_id}/subscriptions",
            json=jsonable_encoder(sub, exclude_unset=True),
        )

        if not nef_res.is_success:
            logging.error("Failed to create NEF subscription")
            raise RuntimeError()

        if nef_res.status_code == 201:
            sub = MonitoringEventSubscription.model_validate(nef_res.json())
            assert sub.self is not None
            asyncio.create_task(self.delete_nef_subscription(sub.self))
            raise RuntimeError("Expected report received subscription")

        report = MonitoringEventReport.model_validate(nef_res.json())
        assert report.roamingStatus is not None

        res = RoamingStatusResponse(
            lastStatusTime=datetime.now(),
            roaming=report.roamingStatus,
        )

        if report.roamingStatus and report.plmnId is not None:
            res.countryCode = report.plmnId.mcc

        return res
