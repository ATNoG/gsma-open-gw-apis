from abc import ABC, abstractmethod

from app.schemas.device import Device
from app.schemas.reachability_status import ReachabilityStatusResponse


class ReachabilityStatusInterface(ABC):
    @abstractmethod
    async def get_reachability_status(
        self, device: Device
    ) -> ReachabilityStatusResponse:
        pass
