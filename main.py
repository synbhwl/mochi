from fastapi import FastAPI
from routers.shorten import router as shorten
from routers.analytics import router as analytics
from routers.redirect import router as redirect


app = FastAPI()

app.include_router(shorten)
app.include_router(analytics)
app.include_router(redirect)
