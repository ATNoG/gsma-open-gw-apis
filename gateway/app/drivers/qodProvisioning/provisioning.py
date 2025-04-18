import logging

from app.interfaces.qodProvisioning import QoDProvisioningAbstractInterface

from app.schemas.qodProvisioning import (
    CreateProvisioning,
    ProvisioningInfo,
    RetrieveProvisioningByDevice,
)

LOG = logging.getLogger(__name__)


class QoDProvisioningInterface(QoDProvisioningAbstractInterface):
    async def crate_provisioning(self, req: CreateProvisioning) -> ProvisioningInfo:
        raise NotImplementedError

    async def get_qod_information_by_id(self, id: str) -> ProvisioningInfo:
        raise NotImplementedError

    async def delete_qod_provisioning(self, id: str) -> ProvisioningInfo:
        raise NotImplementedError

    async def get_qod_information_device(
        self, device: RetrieveProvisioningByDevice
    ) -> ProvisioningInfo:
        raise NotImplementedError
