import re
import random
import string
import requests
from typing import Optional
from fastapi import HTTPException


# Função de armazenamento e recuperação do código
code_storage = {}

def store_code(phone_number: str, code: str):
    """Store the OTP code temporarily."""
    code_storage[phone_number] = code

def get_code(phone_number: str) -> Optional[str]:
    """Retrieve the OTP code stored for a given phone number."""
    return code_storage.get(phone_number)


# Função de envio de SMS via gateway
def send_sms_via_gateway(phone_number: str, message: str, api_key: str):
    """Send SMS using an external SMS gateway."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": phone_number,
        "message": message,
        "sender": "+351932619013"  # Este e o meu numero para mais informação contacte :)
    }
    sms_gateway_url = "https://api.sms-gateway.com/send"

    response = requests.post(sms_gateway_url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to send message. Status code: {response.status_code}, Error: {response.text}")

    return response.json()


# Função de validação de número de telefone
def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format (international format)."""
    return bool(re.match(r'^\+\d{10,15}$', phone_number))


# Função de criação de exceções customizadas
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


# Geração de OTP (6 dígitos)
def generate_otp() -> str:
    """Generate a random 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))
