import logging
import httpx
from app.schemas.location import Point
from app.settings import settings
from app.models.truck import Truck


class ReachabilityService:

    def __init__(self) -> None:

        logging.warning(settings.gateway_url)
        self.httpx_client = httpx.AsyncClient(base_url=str(settings.gateway_url))

    async def reachability_retrieve(self, truck: Truck) -> bool:
        data = {
            "device": {
                "phoneNumber": truck.phoneNumber,
            },
        }

        doc = await self.httpx_client.post(
            url="/device-reachability-status/v1/retrieve", json=data
        )

        return doc.json().get("reachable")


reachability_service = ReachabilityService()
