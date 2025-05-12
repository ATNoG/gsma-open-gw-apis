from typing import Annotated

from fastapi import Depends

from app.drivers.qodProvisioning import get_qodProvisioning_interface
from app.drivers.qodProvisioning.nef.nef_interface import NEFQoDProvisioningInterface


QodProvisioningInterfaceDep = Annotated[
    NEFQoDProvisioningInterface, Depends(get_qodProvisioning_interface)
]
