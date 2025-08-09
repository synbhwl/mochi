from fastapi import (
    Depends,
    HTTPException,
    status,
    Query,
    APIRouter,
    Request
)
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional
import secrets
import os
from dotenv import load_dotenv
import logging
from datetime import timedelta, datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.database import Url_table, create_session

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

limiter = Limiter(key_func=get_remote_address)


class Url_req(BaseModel):
    long: str
    custom_code: Optional[str] = Field(default=None)
    expiry: Optional[str] = Field(default=None)


def generate_code(length: int = 6) -> str:
    code = str(secrets.token_urlsafe(length))[:length]
    return code


def get_expiry_time(period: str):
    expiry_map = {
        "1min": timedelta(minutes=1),  # remove this !
        "1h": timedelta(hours=1),
        "1d": timedelta(days=1),
        "1w": timedelta(days=7),
        "1m": timedelta(days=30)
    }

    if period is None:
        return None
    delta = expiry_map.get(period.lower())
    if delta is None:
        return ValueError("err: period code not recognised, choose one from 1h, 1d, 1w, 1m")
    return datetime.utcnow() + delta


@router.post('/shorten')
@limiter.limit("5/minute")
async def shorten_url(
    request: Request,
    url: Url_req,
    session: Session = Depends(create_session)
):
    if not url:
        logger.error("err: missing field in request body 'url'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="""err: missing field in request body 'url', eg: '{"url":"your url"}'""")

    if url.expiry:
        try:
            expiry_on = get_expiry_time(url.expiry)
        except ValueError as e:
            logger.error(str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if url.custom_code:
        if session.exec(select(Url_table).where(Url_table.code == url.custom_code)).first():
            logger.error("err: user typed custom_code that is already in use")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="err: custom_code already in use, try another")
        else:
            code = url.custom_code
    else:
        code = generate_code()
    newURL = Url_table(
        long=url.long,
        code=code,
        expiry=expiry_on
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
            detail="err: database error while trying to add new URL")

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
@limiter.limit("5/minute")
async def direct_shortener(
    request: Request,
    url: Optional[str] = Query(None),
    custom_code: Optional[str] = Query(None),
    expiry: Optional[str] = Query(None),
    session: Session = Depends(create_session)
):
    if url:
        if custom_code:
            if session.exec(select(Url_table).where(Url_table.code == custom_code)).first():
                logger.error("err: user typed custom_code that is already in use")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="err: custom_code already in use, try another")
            else:
                code = custom_code

        else:
            code = generate_code()

        if expiry:
            try:
                expiry_on = get_expiry_time(expiry)
            except ValueError as e:
                logger.error(str(e))
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        else:
            expiry_on = None

        newURL = Url_table(
            long=url,
            code=code,
            expiry=expiry_on
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
                detail="err: database error while trying to add new URL")

        short_url = f"{base_url}/{code}"
        return {"short_url": short_url}
    else:
        return RedirectResponse(url="/home")
