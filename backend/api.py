"""FastAPI-applikation med router-registrering och CORS."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import APP_VERSION, settings
from core.exceptions import register_exception_handlers
from core.routers.system import router as system_router
from database import create_db_and_tables
from logging_config import setup_logging
from modules.registry import register_modules


# lifespan är en async context manager som FastAPI kör som ett skal runt hela serverns livstid:
# startup-logik före yield, server kör under yield, shutdown-logik efter yield.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup/shutdown-händelser."""
    setup_logging()
    await create_db_and_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(system_router)
register_modules(app)
