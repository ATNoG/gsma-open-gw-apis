from abc import ABC, abstractmethod

from app.schemas.device import Device
from app.schemas.quality_on_demand import (
    CreateSession,
    ExtendSessionDuration,
    SessionInfo,
)


class SessionConflict(Exception):
    pass


class QoDInterface(ABC):
    @abstractmethod
    async def create_provisioning(
        self, req: CreateSession, device: Device
    ) -> SessionInfo:
        pass

    @abstractmethod
    async def get_qod_information_by_id(self, id: str) -> SessionInfo:
        pass

    @abstractmethod
    async def delete_qod_session(self, id: str) -> SessionInfo:
        pass

    @abstractmethod
    async def extend_session(self, id: str, req: ExtendSessionDuration) -> SessionInfo:
        pass

    @abstractmethod
    async def get_qod_information_device(self, device: Device) -> SessionInfo:
        pass
