from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.health import router as health_router

from app.routers.tickets import router as tickets_router
from app.routers.meta import router as meta_router

app = FastAPI()

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(meta_router)