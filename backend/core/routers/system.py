"""Systemroutrar — domän-oberoende endpoints för drift och övervakning."""

from fastapi import APIRouter

from config import APP_VERSION, settings

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness-check för Docker healthcheck och övervakning."""
    return {"status": "ok"}


@router.get("/version")
def version() -> dict[str, str]:
    """Returnerar applikationens namn och version."""
    return {"name": settings.APP_NAME, "version": APP_VERSION}
