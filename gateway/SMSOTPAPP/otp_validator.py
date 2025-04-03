from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/one-time-password-sms/v1.1.0-rc.1")

# Mock database
validation_attempts = {}
otp_storage = {}

class ValidateCodeBody(BaseModel):
    authenticationId: str
    code: str
    phoneNumber: str

def create_exception(status_code: int, error_code: str, message: str):
    """Helper to create consistent error responses"""
    return HTTPException(
        status_code=status_code,
        detail={
            "status": status_code,
            "code": error_code,
            "message": message
        }
    )

def has_exceeded_attempts(auth_id: str) -> bool:
    if auth_id not in validation_attempts:
        return False
    return validation_attempts[auth_id] >= 3
#Mock
def is_expired(auth_id: str) -> bool:
    #expiration time = 5 minutos
    return False

def get_code(phone_number: str) -> Optional[str]:
    return otp_storage.get(phone_number)


# Mock 
def max_otp_codes_exceeded(phone_number: str) -> bool:
    return False
#Mock
def is_phone_number_not_allowed(phone_number: str) -> bool:
    return False
#Mock
def is_phone_number_blocked(phone_number: str) -> bool:
    return False

@router.post('/validate-code', status_code=204)
def validate_code(
    request: ValidateCodeBody, 
    x_correlator: Optional[str] = Header(None)
):
    
    # Input validation
    if not request.authenticationId or not request.code or not request.phoneNumber:
        raise create_exception(
            400,
            "INVALID_ARGUMENT",
            "Client specified an invalid argument, request body or query param."
        )
    
    # Track validation attempts
    if request.authenticationId not in validation_attempts:
        validation_attempts[request.authenticationId] = 0
    validation_attempts[request.authenticationId] += 1
    
    # Business rule validations
    if has_exceeded_attempts(request.authenticationId):
        raise create_exception(
            400,
            "ONE_TIME_PASSWORD_SMS.VERIFICATION_FAILED",
            "The maximum number of attempts for this authenticationId was exceeded without providing a valid OTP"
        )

    if is_expired(request.authenticationId):
        raise create_exception(
            400,
            "ONE_TIME_PASSWORD_SMS.VERIFICATION_EXPIRED",
            "The authenticationId is no longer valid"
        )
    
    if max_otp_codes_exceeded(request.phoneNumber):
        raise create_exception(
            403,
            "ONE_TIME_PASSWORD_SMS.MAX_OTP_CODES_EXCEEDED",
            "Too many OTPs have been requested for this MSISDN. Try later."
        )
    
    if is_phone_number_not_allowed(request.phoneNumber):
        raise create_exception(
            403,
            "ONE_TIME_PASSWORD_SMS.PHONE_NUMBER_NOT_ALLOWED",
            "Phone_number can't receive an SMS due to business reasons in the operator."
        )
    
    if is_phone_number_blocked(request.phoneNumber):
        raise create_exception(
            403,
            "ONE_TIME_PASSWORD_SMS.PHONE_NUMBER_BLOCKED",
            "Phone_number is blocked to receive SMS due to any blocking business reason in the operator."
        )

    # OTP validation
    stored_code = get_code(request.phoneNumber)
    if stored_code is None:
        raise create_exception(
            401,
            "EXPIRED_CODE",
            "Request not authenticated due to missing, invalid, or expired credentials."
        )

    if stored_code != request.code:
        raise create_exception(
            400,
            "ONE_TIME_PASSWORD_SMS.INVALID_OTP",
            "The provided OTP is not valid for this authenticationId"
        )
    
    # Successful validation - return 204 with headers
    headers = {}
    if x_correlator:
        headers["x-correlator"] = x_correlator
    
    return None, headers