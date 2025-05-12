from abc import ABC, abstractmethod
from typing import Optional
from app.schemas.device import Device
from app.schemas.location import Location


class LocationInterface(ABC):
    @abstractmethod
    async def retrieve_location(
        self, device: Device, max_age: Optional[int], max_surface: Optional[int]
    ) -> Location:
        pass
