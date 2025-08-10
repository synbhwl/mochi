from fastapi import APIRouter, Depends
from pydantic import BaseModel
from core.database import Url_table, Clicks, Session, create_session
from urllib.parse import urlparse
from sqlmodel import delete

router = APIRouter()

class Url_in_Body(BaseModel):
    url: str

@router.delete("/delete")
def delete_url(
    url: Url_in_Body,
    session: Session = Depends(create_session)
):
    code = urlparse(url.url).path.strip('/')
    try:
        session.exec(delete(Clicks).where(Clicks.url_code == code))
        session.exec(delete(Url_table).where(Url_table.code == code))
        session.commit()
    except Exception as e:
        logger.error(f"err: error while deleting url: {str(e)}")

    return {"message":"success: url deleted successfully"}