import httpx
from app.schemas.location import Point
from app.settings import settings
from app.models.truck import Truck


class LocationService:

    def __init__(self) -> None:
        self.httpx_client = httpx.AsyncClient(base_url=str(settings.gateway_url))

    async def location_retrieval(self, truck: Truck) -> Point:
        data = {
            "device": {
                "phoneNumber": truck.phoneNumber,
            },
            "maxAge": 0,
            "maxSurface": 0,
        }

        doc = await self.httpx_client.post(
            url="/location_retrieval/v0.4/retrieve", json=data
        )

        point = doc.json().get("area").get("center")

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
            "maxSurface": 0,
        }

        doc = await self.httpx_client.post(
            url="/location_retrieval/v2/verify", json=data
        )

        result = doc.json().get("verificationResult")

        return result == "TRUE"


location_service = LocationService()
