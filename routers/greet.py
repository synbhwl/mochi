# i am intentionally violating REST principles and SoC
# due to constraints i have, namely
# external cron jobs are ineffecient on free tiers
# other alternatives i am aware of are not clean or simple enough

# that is why, i will be writing a database cleanup function
# it'll be implemented everytime someone hits the home page
# would've been better had i put it in a route with more possible traffic
# but they are already cluttered enough, furthermore i have also violated REST and SoC in another place
# to implement the direct_shortener, so i came to this decision

from fastapi import APIRouter, Depends
from sqlmodel import Session, delete, select, and_
from datetime import datetime
from core.database import Url_table, Clicks, create_session
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def database_cleanup(session: Session):
    time_right_now = datetime.utcnow().isoformat()
    try:
        session.exec(delete(Clicks).where(
            Clicks.url_code.in_(
                select(Url_table.code).where(and_(Url_table.expiry.is_not(None), Url_table.expiry < time_right_now))
            )
        ))
        session.exec(delete(Url_table).where(and_(Url_table.expiry.is_not(None), Url_table.expiry < time_right_now)))

        session.commit()
    except Exception as e:
        logger.error(f"err: error while cleaning database: {str(e)}")


@router.get("/")
async def show_home_page(session: Session = Depends(create_session)):
    database_cleanup(session)  # this needs to be reconsidered
    return "welcome to mochi"
