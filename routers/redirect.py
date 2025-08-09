from fastapi import (
    Depends,
    HTTPException,
    status,
    APIRouter,
    Request
)
from fastapi.responses import RedirectResponse
from pydantic import Field
from datetime import datetime
from dotenv import load_dotenv
import logging
from slowapi.util import get_remote_address

from core.database import Url_table, Clicks, create_session

from sqlmodel import SQLModel, create_engine, Field, Session, select, func  # noqa

load_dotenv()
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


@router.get('/{code}')
async def redirect(
    request: Request,
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

    if result.expiry is not None and result.expiry < datetime.utcnow():
        logger.error("err: url expired")
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="err: url expired")

    time = datetime.utcnow().isoformat()
    visitor_id = get_remote_address(request)
    click = Clicks(timestamp=time, url_code=code, visitor_id=visitor_id)
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
