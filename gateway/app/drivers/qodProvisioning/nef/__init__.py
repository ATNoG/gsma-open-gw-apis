from app.settings import QodProvisioningBackend, settings

from .nef_interface import NEFQoDProvisioningInterface

if settings.qod_provisioning.backend != QodProvisioningBackend.Nef:
    raise RuntimeError("QoD provisioning NEF driver instantiated but backend isn't nef")

nef_qod_provisioning_interface = NEFQoDProvisioningInterface(
    settings.qod_provisioning.nef, str(settings.gateway_public_url)
)
