from abc import ABC, abstractmethod
from typing import List

from app.schemas.qos_profiles import QosProfile, QosProfileDeviceRequest


class QoSProfileNotFound(Exception):
    pass


class QoSProfilesInterface(ABC):
    @abstractmethod
    async def get_qos_profiles(self, req: QosProfileDeviceRequest) -> List[QosProfile]:
        pass
