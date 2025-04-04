# ruff: noqa: E402

import pytest
from pytest_mock import MockerFixture

from app.settings import OTPBackend, SMSBackend, settings

settings.sms_otp.sms_backend = SMSBackend.Mock
settings.sms_otp.otp_backend = OTPBackend.Memory

# Settings need to be set before importing anything else

from fastapi.testclient import TestClient

from app.main import app
from app.interfaces.otp import OTPInterface
from app.drivers.otp import get_otp_driver
from app.drivers.sms import get_sms_driver

client = TestClient(app)


def mock_otp():
    class MockOTP(OTPInterface):
        async def generate_otp(self, code_size: int) -> str:
            return "1234"

        async def generate_authentication_id(self) -> str:
            return "12345678-1234-5678-1234-567812345678"

        async def store_otp(
            self,
            authentication_id: str,
            code: str,
            otp_max_attempts: int,
            expires_secs: int,
        ) -> None:
            pass

        async def verify_otp(self, authentication_id: str, code: str) -> None:
            pass

    return MockOTP()


app.dependency_overrides[get_otp_driver] = mock_otp


@pytest.mark.anyio
async def test_send_code(mocker: MockerFixture) -> None:
    spy = mocker.spy(await get_sms_driver(), "send_sms")

    response = client.post(
        "/one-time-password-sms/v1/send-code",
        json={"phoneNumber": "+15555", "message": "A message {{code}}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "authenticationId": "12345678-1234-5678-1234-567812345678"
    }

    spy.assert_called_once_with("+15555", "A message 1234")
