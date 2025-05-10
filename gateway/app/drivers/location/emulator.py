from datetime import datetime
import logging
from os import device_encoding
import httpx
from pydantic import AnyHttpUrl
from fastapi import HTTPException

from app.drivers.nef_auth import NEFAuth
from app.interfaces.location import LocationInterface
from app.schemas.location import Location, Circle, Point, Polygon
from app.schemas.device import Device


class NEFEmulatorDriver(LocationInterface):
    def __init__(self, nef_url: AnyHttpUrl, nef_auth: NEFAuth) -> None:
        super().__init__()
        self.httpx_client = httpx.AsyncClient(base_url=str(nef_url), auth=nef_auth)

    async def retrieve_location(
        self, device: Device, max_age: int, max_surface: int
    ) -> Location:

        data = {
            "monitoringType": "LOCATION_REPORTING",
            "notificationDestination": "https://0.0.0.0",
            "maximumNumberOfReports": 1,
        }

        if device.phoneNumber is not None:
            data["msisdn"] = device.phoneNumber.lstrip("+")
        elif device.ipv4Address is not None:
            data["ipv4Addr"] = str(device.ipv4Address.publicAddress)
        elif device.ipv6Address is not None:
            data["ipv6Addr"] = str(device.ipv6Address)
        elif device.networkAccessIdentifier is not None:
            data["externalId"] = device.networkAccessIdentifier

        url = "/nef/api/v1/3gpp-monitoring-event/v1/myNetApp/subscriptions"

        logging.debug("Querying the NEF Emulator at %s with data %s", url, data)

        doc = self.httpx_client.post(
            url,
            json=data,
        )

        doc = await doc
        if doc.status_code != httpx.codes.OK:
            raise HTTPException(
                status_code=doc.status_code, detail=doc.json()["detail"]
            )

        doc = doc.json()

        print(doc)
        area = doc["locationInfo"]["geographicArea"]

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
