import re
from typing import Optional
import requests
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

router = APIRouter(prefix="/one-time-password-sms/v1.1.0-rc.1")

# Simulação de armazenamento do código temporário (substituir por Redis ou banco de dados)
code_storage = {}

def store_code(phone_number: str, code: str):
    """Store the OTP code temporarily."""
    code_storage[phone_number] = code

def get_code(phone_number: str) -> Optional[str]:
    """Retrieve the OTP code stored for a given phone number."""
    return code_storage.get(phone_number)

# Mocking API key dar replace no futuro
api_key = "SUA_CHAVE_DE_API"

def send_sms_via_gateway(phone_number: str, message: str):
    """Send SMS using an external SMS gateway."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": phone_number,
        "message": message,
        "sender": "+351932619013"  # este e o meu numero para mais informação contacte :)
    }
    sms_gateway_url = "https://api.sms-gateway.com/send"

    response = requests.post(sms_gateway_url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to send message. Status code: {response.status_code}, Error: {response.text}")

    return response.json()

def send_sms(phone_number: str, message: str):
    """Send SMS using the gateway."""
    return send_sms_via_gateway(phone_number, message)

# Função que cria uma exceptiion response customizada
def create_exception(status_code: int, code: str, message: str):
    """Helper function to raise HTTP exceptions with custom details."""
    raise HTTPException(
        status_code=status_code,
        detail={
            "status": status_code,
            "code": code,
            "message": message
        }
    )

# Feita
def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format (international format)."""
    return bool(re.match(r'^\+\d{10,15}$', phone_number))

# Mock function 
def has_exceeded_attempts(authentication_id: str) -> bool:
    """Check if the authenticationId has exceeded max OTP attempts."""
    return False  # Mocking

# Mock function 
def is_expired(authentication_id: str) -> bool:
    """Check if the authenticationId has expired."""
    return False  # Mocking

# Mock function 
def max_otp_codes_exceeded(phone_number: str) -> bool:
    """Check if the max OTP codes for the phone number have been exceeded."""
    return False  # Mocking

# Mock function
def is_phone_number_blocked(phone_number: str) -> bool:
    """Check if the phone number is blocked from receiving SMS."""
    return False  # Mocking

def is_phone_number_not_allowed(phone_number: str) -> bool:
    """Check if the phone number can't receive SMS due to business reasons."""
    return False  # Mocking


class PhoneNumberRequest(BaseModel):
    """Request body schema for sending SMS."""
    phoneNumber: str
    message: str


class ValidateCodeBody(BaseModel):
    """Request body schema for validating OTP code."""
    authenticationId: str
    code: str
    phoneNumber: str


@router.post('/validate-code')
def validate_code(request: ValidateCodeBody, x_correlator: str = Header(None)):
    """Validate OTP code for a given phone number."""
    
    if not request.authenticationId or not request.code or not request.phoneNumber:
        raise create_exception(
            400,
            "INVALID_ARGUMENT",
            "Client specified an invalid argument, request body or query param."
        )
    
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
    
    return {
        "message": "Código validado com sucesso.",
        "x-correlator": x_correlator
    }
