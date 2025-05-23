from uuid import UUID

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str
    otpId: str
    isVerified: bool = Field(default=False)


class Logged(SQLModel, table=True):
    token: UUID = Field(primary_key=True)
    user: int = Field(foreign_key="user.id")
