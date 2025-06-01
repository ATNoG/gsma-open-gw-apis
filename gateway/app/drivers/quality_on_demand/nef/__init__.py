from app.settings import QodBackend, settings

from .nef_interface import NEFQoDInterface

if settings.qod.backend != QodBackend.Nef:
    raise RuntimeError("QoD NEF driver instantiated but backend isn't nef")

nef_qod_interface = NEFQoDInterface(settings.qod.nef, str(settings.gateway_public_url))
