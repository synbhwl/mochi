from fastapi import FastAPI
from routers.shorten import router as shorten
from routers.analytics import router as analytics
from routers.redirect import router as redirect
from routers.greet import router as greet
# from routers.crud import router as crud
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app.include_router(crud)
app.include_router(greet)
app.include_router(shorten)
app.include_router(analytics)
app.include_router(redirect)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)