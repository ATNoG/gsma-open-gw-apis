import logging
from datetime import datetime
from typing import Optional

from app.interfaces.location import LocationInterface
from app.schemas.common import Point
from app.schemas.device import Device
from app.schemas.location import Circle, Location


class MockLocationDriver(LocationInterface):
    async def retrieve_location(
        self, device: Device, max_age: Optional[int], max_surface: Optional[int]
    ) -> Location:
        logging.info(f"Location was requested for {device}")
        return Location(
            lastLocationTime=datetime.now(),
            area=Circle(center=Point(latitude=23, longitude=23), radius=3),
        )
