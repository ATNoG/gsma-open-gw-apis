import logging
import httpx

from app.models.truck import Truck
from app.settings import settings


class QosService:

    def __init__(self) -> None:
        self.httpx_client = httpx.AsyncClient(base_url=str(settings.gateway_url))

    async def increase_bandwidth(self, truck: Truck) -> str:
        logging.warning("Increasing QoS for Truck with id %s", truck.id)
        data = {
            "device": {
                "phoneNumber": truck.phoneNumber,
            },
            "qosProfile": "fast",
        }

        doc = await self.httpx_client.post(
            url="/qod-provisioning/v0.2/device-qos", json=data
        )

        if not doc.is_success:
            raise RuntimeError("Bandwidth could not be increased: ", doc.json())

        return doc.json().get("provisioningId")

    async def decrease_bandwidth(self, truck: Truck) -> str:
        logging.warning("Decreasing QoS for Truck with id %s", truck.id)
        data = {
            "device": {
                "phoneNumber": truck.phoneNumber,
            },
            "qosProfile": "slow",
        }

        doc = await self.httpx_client.post(
            url="/qod-provisioning/v0.2/device-qos", json=data
        )

        if not doc.is_success:
            raise RuntimeError("Bandwidth could not be increased: ", doc.json())

        return doc.json().get("provisioningId")
