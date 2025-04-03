import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.interfaces.otp import (
    OTPExpiredCodeError,
    OTPInterface,
    OTPInvalidCodeError,
    OTPNotFoundError,
    OTPTooManyAttemptsError,
)


@dataclass
class OTPCell:
    code: str
    otp_remaining_attempts: int
    expires_at: datetime


_storage: dict[str, OTPCell] = {}


class MemoryOTPInterface(OTPInterface):
    async def store_otp(
        self,
        authentication_id: str,
        code: str,
        otp_max_attempts: int,
        expires_secs: int,
    ) -> None:
        _storage[authentication_id] = OTPCell(
            code=code,
            otp_remaining_attempts=otp_max_attempts,
            expires_at=datetime.now() + timedelta(seconds=expires_secs),
        )

    async def verify_otp(self, authentication_id: str, code: str) -> None:
        data = _storage.get(authentication_id)
        if data is None:
            raise OTPNotFoundError()

        if data.expires_at < datetime.now():
            del _storage[authentication_id]
            raise OTPExpiredCodeError()

        data.otp_remaining_attempts -= 1
        if data.otp_remaining_attempts < 0:
            del _storage[authentication_id]
            raise OTPTooManyAttemptsError()

        # Use constant time comparison to prevent timing attacks
        if not hmac.compare_digest(code, data.code):
            raise OTPInvalidCodeError()

        del _storage[authentication_id]
