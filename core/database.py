from sqlmodel import SQLModel, create_engine, Field, Session, select, func  # noqa
from typing import Optional

class Url_table(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    long: str
    code: Optional[str] = Field(default=None, unique=True, index=True)

class Clicks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url_code: str
    timestamp: str

engine = create_engine('sqlite:///data.db')
SQLModel.metadata.create_all(engine)


def create_session() -> Session:
    with Session(engine) as session:
        yield session