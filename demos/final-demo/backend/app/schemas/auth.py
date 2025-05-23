from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    password: str
    phoneNumber: str


class CreateUserResponse(BaseModel):
    id: int
    username: str


class OtpRequest(BaseModel):
    id: int
    code: str


class LoginRequest(BaseModel):
    username: str
    password: str
