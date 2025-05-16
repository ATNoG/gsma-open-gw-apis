from app.settings import settings

from .nef_interface import NEFQoDProvisioningInterface

nef_qod_provisioning_interface = NEFQoDProvisioningInterface(
    settings.qod_provisioning.nef, str(settings.gateway_public_url)
)
