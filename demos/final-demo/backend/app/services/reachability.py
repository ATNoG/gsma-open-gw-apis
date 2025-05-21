import asyncio
import logging
from datetime import datetime

import httpx

from app.models.truck import Truck
from app.schemas.subscriptions import ReachabilityEventType
from app.settings import settings


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

    async def reachability_subscription(self, truck: Truck) -> list[dict]:
        now = datetime.now()

        subscriptions = []

        data = {
            "protocol": "HTTP",
            "sink": f"http://localhost:8069/notification/{truck.id}",
            "types": [ReachabilityEventType.v0_reachability_data],
            "config": {
                "subscriptionDetail": {
                    "device": {"phoneNumber": truck.phoneNumber},
                },
                "subscriptionExpireTime": now.replace(year=now.year + 1).isoformat(),
            },
        }

        res = await self.httpx_client.post(
            "/device-reachability-status-subscriptions/v0.7/subscriptions",
            json=data,
        )

        subscriptions.append(res.json())

        data["types"] = [ReachabilityEventType.v0_reachability_sms]

        res = await self.httpx_client.post(
            "/device-reachability-status-subscriptions/v0.7/subscriptions",
            json=data,
        )

        subscriptions.append(res.json())

        data["types"] = [ReachabilityEventType.v0_reachability_disconnected]

        res = await self.httpx_client.post(
            "/device-reachability-status-subscriptions/v0.7/subscriptions",
            json=data,
        )

        subscriptions.append(res.json())
        return subscriptions

    async def delete_reachability_subscription(self, sub_id: str):
        await self.httpx_client.delete(
            f"/device-reachability-status-subscriptions/v0.7/subscriptions/{sub_id}"
        )


reachability_service = ReachabilityService()
