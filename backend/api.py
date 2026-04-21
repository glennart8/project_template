"""FastAPI-applikation med router-registrering och CORS."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.core.exceptions import register_exception_handlers
from backend.core.routers.system import router as system_router
from backend.database import create_db_and_tables
from backend.logging_config import setup_logging
from backend.modules.registry import register_modules


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Startup/shutdown-händelser."""
    setup_logging()
    await create_db_and_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
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
