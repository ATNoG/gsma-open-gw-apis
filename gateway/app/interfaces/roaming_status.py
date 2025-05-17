from abc import ABC, abstractmethod

from app.schemas.device import Device
from app.schemas.roaming_status import RoamingStatusResponse


class RoamingStatusInterface(ABC):
    @abstractmethod
    async def get_roaming_status(self, device: Device) -> RoamingStatusResponse:
        pass
