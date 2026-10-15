"""FastAPI-applikation och router-registrering."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import APP_VERSION, settings
from core.exceptions import register_exception_handlers
from core.routers.system import router as system_router
from database import create_db_and_tables


# Startup-logik före yield, shutdown-logik efter.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

register_exception_handlers(app)
# Allt under /api, så att proxyn (nginx i drift, Vite i utveckling) kan skicka
# /api till backend och resten till frontend.
app.include_router(system_router, prefix="/api")
