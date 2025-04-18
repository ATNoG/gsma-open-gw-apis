from abc import ABC, abstractmethod

from app.schemas.qodProvisioning import (
    CreateProvisioning,
    ProvisioningInfo,
    RetrieveProvisioningByDevice,
)


class ResourceNotFound(Exception):
    pass


class DeviceNotFound(Exception):
    pass


class QoDProvisioningAbstractInterface(ABC):
    @abstractmethod
    async def crate_provisioning(self, req: CreateProvisioning) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def get_qod_information_by_id(self, id: str) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def delete_qod_provisioning(self, id: str) -> ProvisioningInfo:
        pass

    @abstractmethod
    async def get_qod_information_device(
        self, device: RetrieveProvisioningByDevice
    ) -> ProvisioningInfo:
        pass
