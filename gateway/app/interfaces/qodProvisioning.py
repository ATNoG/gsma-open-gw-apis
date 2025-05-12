from abc import ABC, abstractmethod

from app.schemas.qodProvisioning import (
    TriggerProvisioning,
    ProvisioningInfo,
    RetrieveProvisioningByDevice,
)


class ResourceNotFound(Exception):
    pass


class ProvisioningConflict(Exception):
    pass


class QoDProvisioningInterface(ABC):
    @abstractmethod
    async def create_provisioning(self, req: TriggerProvisioning) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def get_qod_information_by_id(self, id: str) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def delete_qod_provisioning(self, id: str) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def get_qod_information_device(
        self, device_req: RetrieveProvisioningByDevice
    ) -> ProvisioningInfo:
        pass
