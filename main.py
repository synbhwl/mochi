from fastapi import (
    FastAPI,
    Depends
)
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from dotenv import load_dotenv
import secrets
from core.config import get_settings

from sqlmodel import SQLModel, create_engine, Field, Session
settings = get_settings()
app = FastAPI()

base_url = settings.base_url


class url_req(BaseModel):
    long: HttpUrl


class url_table(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    long: str
    code: Optional[str] = Field(default=None, unique=True, index=True)


engine = create_engine('sqlite:///data.db')
SQLModel.metadata.create_all(engine)


def create_session() -> Session:
    with Session(engine) as session:
        yield session


def generate_code(length: int = 6) -> str:
    code = str(secrets.token_urlsafe(length))[:length]
    return code


@app.post('/shorten')
async def shorten_url(
    long: url_req,
    session: Session = Depends(create_session)
):
    code = generate_code()
    newURL = url_table(
        long=str(long),
        code=code
    )

    session.add(newURL)
    session.commit()
    session.refresh(newURL)

    return {"new_url": f"this is you url {base_url}/{code}"}
