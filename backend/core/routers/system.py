"""Systemroutrar — domän-oberoende endpoints för drift och övervakning."""

from fastapi import APIRouter

from backend.config import settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness-check för load balancers och Docker healthcheck."""
    return {"status": "ok"}


@router.get("/version")
async def version() -> dict[str, str]:
    """Returnerar applikationens namn och version."""
    return {"name": settings.APP_NAME, "version": "0.1.0"}
