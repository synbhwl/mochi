from fastapi import FastAPI
from routers.shorten import router as shorten
from routers.analytics import router as analytics
from routers.redirect import router as redirect
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(shorten)
app.include_router(analytics)
app.include_router(redirect)
