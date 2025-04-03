from abc import ABC, abstractmethod

import os
import base64
from uuid import UUID


class OTPNotFoundError(Exception):
    pass


class OTPInvalidCodeError(Exception):
    pass


class OTPExpiredCodeError(Exception):
    pass


class OTPTooManyAttemptsError(Exception):
    pass


class OTPInterface(ABC):
    async def generate_otp(self, code_size: int) -> str:
        # Each base32 letter has 5 bits of information, so in order to obtain
        # a code with size N, ceil(5/8 * N) = ((5 * N) + 7) // 8
        needed_bytes = ((5 * code_size) + 7) // 8
        random_data = os.urandom(needed_bytes)
        raw_code = base64.b32hexencode(random_data).decode("utf-8")
        # Codes might have 1 character more than the requested size, so truncate it
        return raw_code[:code_size]

    async def generate_authentication_id(self) -> str:
        # SAFETY: urandom generates cryptographically secure randomness, and
        #         with 16 bytes, the risk of collision is acceptable.
        return str(UUID(bytes=os.urandom(16), version=4))

    @abstractmethod
    async def store_otp(
        self,
        authentication_id: str,
        code: str,
        otp_max_attempts: int,
        expires_secs: int,
    ) -> None:
        pass

    @abstractmethod
    async def verify_otp(self, authentication_id: str, code: str) -> None:
        pass
