from datetime import datetime

import httpx

from app.models.truck import Truck
from app.schemas.location import Point
from app.schemas.subscriptions import GeofencingEventType
from app.settings import settings


class LocationService:

    def __init__(self) -> None:
        self.httpx_client = httpx.AsyncClient(base_url=str(settings.gateway_url))

    async def location_retrieval(self, truck: Truck) -> Point:
        data = {
            "device": {
                "phoneNumber": truck.phoneNumber,
            },
            "maxAge": 0,
            "maxSurface": 1,
        }

        doc = await self.httpx_client.post(
            url="/location-retrieval/v0.4/retrieve", json=data
        )

        if not doc.is_success:
            raise RuntimeError("Location could not be retrieved: ", doc.json())

        point = Point.model_validate(doc.json().get("area").get("center"))

        return Point(latitude=point.latitude, longitude=point.longitude)

    async def location_verification(
        self, truck: Truck, point: Point, radius: int
    ) -> bool:
        data = {
            "device": {
                "phoneNumber": truck.phoneNumber,
            },
            "area": {
                "areaType": "CIRCLE",
                "center": {
                    "latitude": point.latitude,
                    "longitude": point.longitude,
                },
                "radius": radius,
            },
            "maxAge": 0,
            "maxSurface": 1,
        }

        doc = await self.httpx_client.post(
            url="/location-verification/v2/verify", json=data
        )
        if not doc.is_success:
            raise RuntimeError("Location could not be verified: ", doc.json())

        result = doc.json().get("verificationResult")

        return result == "TRUE"

    async def geofencing_subscription(
        self, truck: Truck, point: Point, radius: int
    ) -> list[dict]:
        now = datetime.now()
        subscriptions = []

        data = {
            "protocol": "HTTP",
            "sink": f"http://localhost:8069/notification/{truck.id}",
            "types": [GeofencingEventType.v0_area_entered],
            "config": {
                "subscriptionDetail": {
                    "device": {"phoneNumber": truck.phoneNumber},
                    "area": {
                        "areaType": "CIRCLE",
                        "center": {
                            "latitude": point.latitude,
                            "longitude": point.longitude,
                        },
                        "radius": radius,
                    },
                },
                "subscriptionExpireTime": now.replace(year=now.year + 1).isoformat(),
            },
        }

        res = await self.httpx_client.post(
            "/geofencing-subscriptions/v0.4/subscriptions",
            json=data,
        )

        subscriptions.append(res.json())

        data["types"] = [GeofencingEventType.v0_area_left]

        res = await self.httpx_client.post(
            "/geofencing-subscriptions/v0.4/subscriptions", json=data
        )

        subscriptions.append(res.json())

        return subscriptions

    async def delete_geofencing_subscription(self, sub_id):
        await self.httpx_client.delete(
            f"/geofencing-subscriptions/v0.4/subscriptions/{sub_id}"
        )


location_service = LocationService()
