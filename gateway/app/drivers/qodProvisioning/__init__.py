from typing import Annotated

from fastapi import Depends

from .provisioning import RedisQoDProvisioningInterface
from app.interfaces.qodProvisioning import QoDProvisioningAbstractInterface

qodProvisioning_interface: QoDProvisioningAbstractInterface = (
    RedisQoDProvisioningInterface()
)


def get_qodProvisioning_interface() -> QoDProvisioningAbstractInterface:
    return qodProvisioning_interface


qodProvisioningInterfaceDep = Annotated[
    QoDProvisioningAbstractInterface, Depends(get_qodProvisioning_interface)
]
