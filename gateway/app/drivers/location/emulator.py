from datetime import datetime
import httpx
from pydantic import AnyHttpUrl
from fastapi import HTTPException

from app.settings import settings
from app.interfaces.location import LocationInterface
from app.schemas.location import Location, Circle, Point, Polygon
from app.schemas.device import Device


class NEFEmulatorDriver(LocationInterface):
    def __init__(self, emulator_url: AnyHttpUrl) -> None:
        super().__init__()

        self.emulator_url = emulator_url
        self.httpx_client = httpx.AsyncClient()

    async def retrieve_location(
        self, device: Device, max_age: int, max_surface: int
    ) -> Location:
        if not device.phoneNumber:
            raise HTTPException(status_code=501, detail="Identifier not implemented")

        data = {
            "analyEvent": "UE_MOBILITY",
            "tgtUe": {"gpsi": device.phoneNumber.lstrip("+")},
            "suppFeat": "a",
        }
        url = (
            f"{self.emulator_url}/api/v1/3gpp-analyticsexposure/v1/{settings.afId}/fetch",
        )

        print("Querying the NEF Emulator at", url, "with data", data)

        doc = self.httpx_client.post(
            f"{self.emulator_url}nef/api/v1/3gpp-analyticsexposure/v1/{settings.afId}/fetch",
            json=data,
        )

        doc = await doc
        if doc.status_code != httpx.codes.OK:
            raise HTTPException(
                status_code=doc.status_code, detail=doc.json()["detail"]
            )

        doc = doc.json()

        print(doc)
        area = doc["ueMobilityInfos"][0]["locInfo"][0]["loc"]["geographicAreas"][0]

        if area["shape"] == "POINT":
            point = area["point"]
            return Location(
                lastLocationTime=datetime.now(),
                area=Circle(
                    center=Point(latitude=point["lat"], longitude=point["lon"]),
                    radius=10,
                ),
            )

        if area["shape"] == "POLYGON":
            return Location(
                lastLocationTime=datetime.now(),
                area=Polygon(boundary=area["pointList"]),
            )

        raise HTTPException(status_code=501, detail="Area response not supported")
