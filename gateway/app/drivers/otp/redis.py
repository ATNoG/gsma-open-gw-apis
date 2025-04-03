import hmac
import logging
from redis.asyncio import WatchError

from app.redis import get_redis
from app.interfaces.otp import (
    OTPInterface,
    OTPInvalidCodeError,
    OTPNotFoundError,
    OTPTooManyAttemptsError,
)

_prefix = "smsotp"
LOG = logging.getLogger(__name__)


class RedisOTPInterface(OTPInterface):
    async def store_otp(
        self,
        authentication_id: str,
        code: str,
        otp_max_attempts: int,
        expires_secs: int,
    ) -> None:
        redis = get_redis()

        key = f"{_prefix}:{authentication_id}"

        p = redis.pipeline()
        p.multi()  # type: ignore [no-untyped-call]
        # All redis functions return an union between the sync and async
        # results making them impossible to typecheck
        await p.hmset(
            key,
            {
                "code": code,
                "remaining_attempts": otp_max_attempts,
            },
        )  # type: ignore [misc]
        await p.expire(key, expires_secs)
        await p.execute()

    async def verify_otp(self, authentication_id: str, code: str) -> None:
        redis = get_redis()

        key = f"{_prefix}:{authentication_id}"

        while True:
            try:
                async with redis.pipeline() as p:
                    await p.watch(key)
                    # All redis functions return an union between the sync and async
                    # results making them impossible to typecheck
                    data = await p.hgetall(key)  # type: ignore [misc]
                    print(data)

                    if data == {}:
                        LOG.debug(
                            "Validate for %s: No OTP data found", authentication_id
                        )
                        raise OTPNotFoundError()

                    # This function isn't typed
                    p.multi()  # type: ignore [no-untyped-call]

                    if int(data["remaining_attempts"]) <= 0:
                        LOG.debug(
                            "Validate for %s: Attempts exceeded", authentication_id
                        )
                        await p.delete(key)
                    else:
                        LOG.debug(
                            "Validate for %s: Decrementing attempts", authentication_id
                        )
                        # All redis functions return an union between the sync and async
                        # results making them impossible to typecheck
                        await p.hincrby(key, "remaining_attempts", -1)  # type: ignore [misc]

                    await p.execute()
                break
            except WatchError:
                LOG.debug("Validate for %s: Watch error, retrying", authentication_id)
                continue

        if int(data["remaining_attempts"]) <= 0:
            raise OTPTooManyAttemptsError()

        # Use constant time comparison to prevent timing attacks
        if not hmac.compare_digest(code, data["code"]):
            raise OTPInvalidCodeError()

        await redis.delete(key)
