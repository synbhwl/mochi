from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Query
)
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
# from dotenv import load_dotenv
import secrets
from core.config import get_settings

from sqlmodel import SQLModel, create_engine, Field, Session, select  # noqa
settings = get_settings()
app = FastAPI()

base_url = settings.base_url


class Url_req(BaseModel):
    long: str


class Url_table(SQLModel, table=True):
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
    url: Url_req,
    session: Session = Depends(create_session)
):
    code = generate_code()
    newURL = Url_table(
        long=url.long,
        code=code
    )

    session.add(newURL)
    session.commit()
    session.refresh(newURL)

    return {"new_url": f"this is you url {base_url}/{code}"}

# violating rest api principles to make a direct shortener


@app.get('/', response_class=HTMLResponse)
async def direct_shortener(
    url: Optional[str] = Query(None),
    session: Session = Depends(create_session)
):
    if url:
        code = generate_code()
        newURL = Url_table(
            long=url,
            code=code
        )

        session.add(newURL)
        session.commit()
        session.refresh(newURL)

        short_url = f"{base_url}/{code}"
        with open('templates/shortened.html', 'r') as f:
            html_content = f.read()
        html_content = html_content.replace("{{short_url}}", short_url)
        return HTMLResponse(content=html_content)
    else:
        with open('templates/home.html', 'r') as f:
            home_content = f.read()
        home_content = home_content.replace("{{base_url}}", base_url)

        return HTMLResponse(content=home_content)


@app.get('/{code}')
async def redirect(
    code: str,
    session: Session = Depends(create_session)
):
    result = session.exec(select(Url_table).where(
        Url_table.code == code)).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no such url found")

    return RedirectResponse(result.long)
