"""Systemroutrar — domän-oberoende endpoints för drift och övervakning."""

from fastapi import APIRouter, Response

from config import APP_VERSION, settings
from core.auth import CurrentUser
from core.dependencies import CurrentUserDep, SessionDep
from database import is_database_up

router = APIRouter(tags=["system"])


@router.get("/health")
def health(session: SessionDep, response: Response) -> dict[str, str]:
    """För Docker och övervakning. 503 om databasen inte svarar."""
    if not is_database_up(session):
        response.status_code = 503
        return {"status": "databasen svarar inte"}
    return {"status": "ok"}


@router.get("/version")
def version() -> dict[str, str]:
    """Returnerar applikationens namn och version."""
    return {"name": settings.APP_NAME, "version": APP_VERSION}


@router.get("/me")
def me(user: CurrentUserDep) -> CurrentUser:
    """Den inloggade användaren, för frontend."""
    return user
