from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import time
from datetime import datetime, timedelta

router = APIRouter(prefix="/one-time-password-sms/v1.1.0-rc.1")

# Mock database for storing OTP data
mock_db = {
    "otp_codes": {},
    "phone_number_attempts": {},
    "phone_number_blocks": set()
}

class PhoneNumberRequest(BaseModel):
    phoneNumber: str
    message: str

def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format according to E.164 standard"""
    return phone_number.startswith('+') and phone_number[1:].isdigit() and len(phone_number) <= 16

def generate_otp() -> str:
    """Generate a 6-digit OTP code"""
    import random
    return ''.join(random.choices('0123456789', k=6))

def store_code(phone_number: str, code: str):
    """Store the OTP code with expiration time (5 minutes)"""
    expiration = datetime.now() + timedelta(minutes=5)
    mock_db["otp_codes"][phone_number] = {
        "code": code,
        "expiration": expiration,
        "attempts": 0
    }

def is_phone_number_blocked(phone_number: str) -> bool:
    """Check if phone number is blocked"""
    return phone_number in mock_db["phone_number_blocks"]

def max_otp_codes_exceeded(phone_number: str) -> bool:
    """Check if too many OTP requests were made for this number"""
    if phone_number not in mock_db["phone_number_attempts"]:
        return False
    
    last_hour = datetime.now() - timedelta(hours=1)
    recent_attempts = [
        ts for ts in mock_db["phone_number_attempts"][phone_number] 
        if ts > last_hour
    ]
    return len(recent_attempts) >= 5  # Max 5 attempts per hour

def track_otp_attempt(phone_number: str):
    """Track OTP attempt for rate limiting"""
    if phone_number not in mock_db["phone_number_attempts"]:
        mock_db["phone_number_attempts"][phone_number] = []
    mock_db["phone_number_attempts"][phone_number].append(datetime.now())

@router.post('/send-code', response_model=dict)
def send_code(
    request: PhoneNumberRequest, 
    x_correlator: Optional[str] = Header(None)
):
    """Mock implementation of SMS OTP sending endpoint"""
    
    # Input validation
    if not request.phoneNumber or not request.message:
        raise HTTPException(
            status_code=400,
            detail={
                "status": 400,
                "code": "INVALID_ARGUMENT",
                "message": "Client specified an invalid argument, request body or query param."
            },
            headers={"x-correlator": x_correlator} if x_correlator else None
        )
    
    if not validate_phone_number(request.phoneNumber):
        raise HTTPException(
            status_code=400,
            detail={
                "status": 400,
                "code": "INVALID_PHONE_NUMBER",
                "message": "The phone number provided is not in a valid format."
            },
            headers={"x-correlator": x_correlator} if x_correlator else None
        )

    # Business rule validations
    if is_phone_number_blocked(request.phoneNumber):
        raise HTTPException(
            status_code=403,
            detail={
                "status": 403,
                "code": "ONE_TIME_PASSWORD_SMS.PHONE_NUMBER_BLOCKED",
                "message": "Phone_number is blocked to receive SMS due to any blocking business reason in the operator."
            },
            headers={"x-correlator": x_correlator} if x_correlator else None
        )
    
    if max_otp_codes_exceeded(request.phoneNumber):
        raise HTTPException(
            status_code=403,
            detail={
                "status": 403,
                "code": "ONE_TIME_PASSWORD_SMS.MAX_OTP_CODES_EXCEEDED",
                "message": "Too many OTPs have been requested for this MSISDN. Try later."
            },
            headers={"x-correlator": x_correlator} if x_correlator else None
        )

    # Generate and store OTP
    otp_code = generate_otp()
    store_code(request.phoneNumber, otp_code)
    track_otp_attempt(request.phoneNumber)
    
    # Mock SMS sending
    authentication_id = str(uuid.uuid4())
    message_content = request.message.replace("{{code}}", otp_code)
    
    # Simulate SMS sending delay
    time.sleep(0.5)
    
    # Log mock SMS details
    print("\n=== MOCK SMS SENT ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"To: {request.phoneNumber}")
    print(f"Message: {message_content}")
    print(f"OTP Code: {otp_code}")
    print(f"Auth ID: {authentication_id}")
    print(f"X-Correlator: {x_correlator}")
    print("====================\n")
    
    response = {
        "authenticationId": authentication_id
    }
    
    if x_correlator:
        return {"x-correlator": x_correlator, **response}
    return response