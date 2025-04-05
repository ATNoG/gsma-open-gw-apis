from abc import ABC, abstractmethod
from app.schemas.device import Device
from app.schemas.location import Location


class LocationInterface(ABC):
    @abstractmethod
    async def retrieve_location(
        self, device: Device, max_age: int, max_surface: int
    ) -> Location:
        pass
