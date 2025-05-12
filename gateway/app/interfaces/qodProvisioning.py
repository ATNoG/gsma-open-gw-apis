from abc import ABC, abstractmethod

from app.schemas.device import Device
from app.schemas.qodProvisioning import (
    TriggerProvisioning,
    ProvisioningInfo,
)


class ResourceNotFound(Exception):
    pass


class ProvisioningConflict(Exception):
    pass


class QoDProvisioningInterface(ABC):
    @abstractmethod
    async def create_provisioning(
        self, req: TriggerProvisioning, device: Device
    ) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def get_qod_information_by_id(self, id: str) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def delete_qod_provisioning(self, id: str) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def get_qod_information_device(self, device: Device) -> ProvisioningInfo:
        pass
