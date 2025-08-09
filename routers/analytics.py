from fastapi import (
    Depends,
    HTTPException,
    status,
    APIRouter
)
from fastapi.responses import Response
from pydantic import Field
from urllib.parse import urlparse
import json
from dotenv import load_dotenv
import logging

from core.database import Clicks, create_session

from sqlmodel import SQLModel, create_engine, Field, Session, select, func  # noqa

load_dotenv()
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


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
