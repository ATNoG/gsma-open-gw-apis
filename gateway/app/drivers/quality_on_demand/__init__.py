from typing import Annotated

from fastapi import Depends

from app.interfaces.quality_on_demand import QoDInterface
from app.settings import QodBackend, settings

qod_interface: QoDInterface


match settings.qod.backend:
    case QodBackend.Nef:
        from .nef import nef_qod_interface

        qod_interface = nef_qod_interface


def get_qod_interface() -> QoDInterface:
    return qod_interface


QodInterfaceDep = Annotated[QoDInterface, Depends(get_qod_interface)]
