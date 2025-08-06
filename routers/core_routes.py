from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Query,
    APIRouter
)
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from pydantic import BaseModel, Field
from typing import Optional
import secrets
from core.config import get_settings
from datetime import datetime
from urllib.parse import urlparse
import json

from core.database import Url_table, Clicks, create_session

from sqlmodel import SQLModel, create_engine, Field, Session, select, func  # noqa
settings = get_settings()
# app = FastAPI()
router = APIRouter()

base_url = settings.base_url


# url_req parses the url from the body of the post request
class Url_req(BaseModel):
    long: str


def generate_code(length: int = 6) -> str:
    code = str(secrets.token_urlsafe(length))[:length]
    return code

# requires json body


@router.post('/shorten')
async def shorten_url(
    url: Url_req,  # takes the whole url as an object instance of url_req
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
# i made it so the user can type the url in the address bar along with the query param
# and directly get a shortened link with needing any further frontend or forms
# making it accessible even to mobile users

# the route also violates the separation of concerns
# since i am trying to handle html, home and shortening at the same time
# however i have tried keeping it as explicit as possible
# and have avoided excessive modularization of it


@router.get('/', response_class=HTMLResponse)
async def direct_shortener(
    # the url query parameter is an optional param with default as none
    url: Optional[str] = Query(None),
    # if the param is present, it executes the shortening logic
    # otherwise takes you to a home page
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


# this route returns a basic analytics json schema for now
@router.get('/analytics')
async def show_analytics(url: str, session: Session = Depends(create_session)):
    # this parses the path from the url and remove the '/'
    code = urlparse(url).path.strip('/')

    clicks = session.exec(select(func.count()).where(
        Clicks.url_code == code)).first()  # counts the number of clicks

    history = session.exec(select(Clicks).where(
        Clicks.url_code == code)).all()  # returns result object
    # of all the Clicks that had the particular code

    # takes out only the time stamps
    timestamps = [t.timestamp for t in history]

    analytics = {
        "shortened_url": url,
        "total_clicks": clicks,
        "time_history": timestamps
    }
    return Response(
        content=json.dumps(analytics, indent=2),  # this is for pretty print
        media_type="application/json"
    )

# this route handles the rediction of the user + the incrementation logic of the counting feature
# it adds a click object everytime a the shortened link is clicked/used


@router.get('/{code}')
async def redirect(
    code: str,
    session: Session = Depends(create_session)
):
    result = session.exec(select(Url_table).where(
        Url_table.code == code)).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no such url found")

    time = datetime.utcnow().isoformat()
    click = Clicks(timestamp=time, url_code=code)
    session.add(click)
    session.commit()
    session.refresh(click)

    return RedirectResponse(result.long)
