from fastapi import Depends

from typing import Annotated

from app.settings import OTPBackend, settings
from app.interfaces.otp import OTPInterface

from .redis import RedisOTPInterface
from .memory import MemoryOTPInterface

otp_interface: OTPInterface
match settings.sms_otp.otp_backend:
    case OTPBackend.Memory:
        otp_interface = MemoryOTPInterface()
    case OTPBackend.Redis:
        otp_interface = RedisOTPInterface()
        pass


async def get_otp_driver() -> OTPInterface:
    return otp_interface


OTPInterfaceDep = Annotated[OTPInterface, Depends(get_otp_driver)]
