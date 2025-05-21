import logging
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import StaticPool

sqlite_url = "sqlite://"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, poolclass=StaticPool)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
