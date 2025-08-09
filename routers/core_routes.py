from fastapi import (
    Depends,
    HTTPException,
    status,
    Query,
    APIRouter
)
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, Field
from typing import Optional
import secrets
from datetime import datetime
from urllib.parse import urlparse
import json
import os
from dotenv import load_dotenv
import logging

from core.database import Url_table, Clicks, create_session

from sqlmodel import SQLModel, create_engine, Field, Session, select, func  # noqa

load_dotenv()
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

base_url = os.getenv("BASE_URL").strip()
if not base_url:
    logger.error("err: base_url missing in .env")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="err: base_url missing")


class Url_req(BaseModel):
    long: str


def generate_code(length: int = 6) -> str:
    code = str(secrets.token_urlsafe(length))[:length]
    return code


@router.post('/shorten')
async def shorten_url(
    url: Url_req,
    session: Session = Depends(create_session)
):
    if not url:
        logger.error("err: missing field in request body 'url'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="""err: missing field in request body 'url',
            eg: '{"url":"your url"}'""")

    code = generate_code()
    newURL = Url_table(
        long=url.long,
        code=code
    )
    try:
        session.add(newURL)
        session.commit()
        session.refresh(newURL)
    except Exception as e:
        logger.error(
            f"err: database error while trying to add new URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"err: database error while trying to add new URL: {str(e)}")

    return {"new_url": f"this is you url {base_url}/{code}"}

# violating rest api principles to make a direct shortener
# i made it so the user can type the url in the address bar
# along with the query param
# and directly get a shortened link with needing any further frontend or forms
# making it accessible even to mobile users

# the route also violates the separation of concerns
# since i am trying to handle html, home and shortening at the same time
# however i have tried keeping it as explicit as possible
# and have avoided excessive modularization of it


@router.get('/')
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
        try:
            session.add(newURL)
            session.commit()
            session.refresh(newURL)
        except Exception as e:
            logger.error(
                f"err: database error while trying to add new URL:{str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"err: database error while trying to add new URL: {str(e)}")

        short_url = f"{base_url}/{code}"
        return {"short_url": short_url}
    else:
        return "welcome to mochi"


# this route returns a basic analytics json schema for now
@router.get('/analytics')
async def show_analytics(url: str, session: Session = Depends(create_session)):
    if not url:
        logger.error("err: missing query parameter 'url'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="err: missing query parameter 'url', eg: /analytics?url=your_url")

    code = urlparse(url).path.strip('/')
    if not code:
        logger.error("err: code missing at the end of shortened url")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="err: code missing at the end of shortened url, eg: /U4q0dX")
    try:
        clicks = session.exec(select(func.count()).where(
            Clicks.url_code == code)).first()

        history = session.exec(select(Clicks).where(
            Clicks.url_code == code)).all()
    except Exception as e:
        logger.error(
            f"err: either total_clicks or timestamp_history doesn't exist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"err: either total_clicks or timestamp_history doesn't exist: {str(e)}")

    timestamps = [t.timestamp for t in history]

    analytics = {
        "shortened_url": url,
        "total_clicks": clicks,
        "time_history": timestamps
    }
    return Response(
        content=json.dumps(analytics, indent=2),
        media_type="application/json"
    )


@router.get('/{code}')
async def redirect(
    code: str,
    session: Session = Depends(create_session)
):
    if not code:
        logger.error("err: missing path parameter 'code'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="err: missing path parameter 'code', eg: /U4q0dX")

    result = session.exec(select(Url_table).where(
        Url_table.code == code)).first()
    if result is None:
        logger.error("err: no such url found in the database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="err: no such url found in the database")

    time = datetime.utcnow().isoformat()
    click = Clicks(timestamp=time, url_code=code)
    try:
        session.add(click)
        session.commit()
        session.refresh(click)
    except Exception as e:
        logger.error(
            f"err: database error while trying to add new click:{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"err: database error while trying to add new click: {str(e)}")

    return RedirectResponse(result.long)
