"""FastAPI-applikation och router-registrering."""

from fastapi import FastAPI

from config import APP_VERSION, settings
from core.exceptions import register_exception_handlers
from core.routers.system import router as system_router

# API-dokumentationen (/docs) visar hela API:et; den stängs av i drift.
docs_on = settings.ENVIRONMENT != "production"

app = FastAPI(
    title=settings.APP_NAME,
    version=APP_VERSION,
    docs_url="/api/docs" if docs_on else None,
    redoc_url=None,
    openapi_url="/api/openapi.json" if docs_on else None,
)

register_exception_handlers(app)
# Allt under /api, så att proxyn (Caddy i drift, Vite i utveckling) kan skicka
# /api till backend och resten till frontend.
app.include_router(system_router, prefix="/api")
