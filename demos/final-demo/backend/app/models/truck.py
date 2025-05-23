from sqlmodel import Field, SQLModel


class Truck(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    phoneNumber: str
    isQueued: bool = Field(default=False)
    isReachable: bool = Field(default=False)
