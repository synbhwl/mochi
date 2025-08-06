from fastapi import FastAPI
from routers.core_routes import router as core_routes
app = FastAPI()

app.include_router(core_routes)