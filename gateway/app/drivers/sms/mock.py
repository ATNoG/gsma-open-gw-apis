from app.interfaces.sms import SMSInterface


class MockSMSInterface(SMSInterface):
    async def send_sms(self, msisdn: str, text: str) -> None:
        print(f"Would send SMS to {msisdn}: {text}")
