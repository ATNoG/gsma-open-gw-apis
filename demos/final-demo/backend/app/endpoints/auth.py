import uuid
from http import HTTPStatus
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.models.auth import Logged, User
from app.schemas.auth import (
    CreateUserRequest,
    CreateUserResponse,
    LoginRequest,
    LoginResponse,
    OtpRequest,
    UserRequest,
    UserResponse,
)
from app.services.sms import sms_service
from app.session import get_session

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register(
    item_in: CreateUserRequest, db: Session = Depends(get_session)
) -> CreateUserResponse:
    authId = await sms_service.send_otp(item_in.phoneNumber)
    user = User(
        username=item_in.username,
        password=item_in.password,
        otpId=authId,
        phoneNumber=item_in.phoneNumber,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    if user.id is None:
        raise HTTPException(status_code=500, detail="An error has occured")

    return CreateUserResponse(id=user.id, username=user.username)


@router.post("/verify", status_code=HTTPStatus.NO_CONTENT)
async def verify(item_in: OtpRequest, db: Session = Depends(get_session)) -> None:
    user = db.get(User, item_in.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    valid = await sms_service.verify_otp(user.otpId, item_in.code)

    if valid:
        user.isVerified = True
        db.add(user)
        db.commit()


@router.post("/login")
def login(item_in: LoginRequest, db: Session = Depends(get_session)) -> LoginResponse:
    stmt = (
        select(User)
        .where(User.username == item_in.username)
        .where(User.password == item_in.password)
        .where(User.isVerified)
    )
    user = db.exec(stmt).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id is None:
        raise HTTPException(status_code=500, detail="An error has occured")

    token = uuid4()
    db.add(Logged(user=user.id, token=token))
    db.commit()

    return LoginResponse(token=str(token))


@router.post("/me")
def me(req: UserRequest, db: Session = Depends(get_session)) -> UserResponse:
    token: uuid.UUID
    try:
        token = uuid.UUID(req.token)
    except ValueError:
        raise HTTPException(400, "Invalid token")

    stmt = (
        select(User)
        .join(Logged)
        .where(Logged.token == token)
        .where(User.id == Logged.user)
    )
    user = db.exec(stmt).first()
    if user is None:
        raise HTTPException(400, "Invalid token")
    return UserResponse(username=user.username, phoneNumber=user.phoneNumber)
