"""Systemroutrar — domän-oberoende endpoints."""

from fastapi import APIRouter

from auth import CurrentUser
from dependencies import CurrentUserDep

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    """Svarar om appen lever. Med databaskontroll: se docs/extra.md."""
    return {"status": "ok"}


@router.get("/me")
def me(user: CurrentUserDep) -> CurrentUser:
    """Den inloggade användaren, för frontend."""
    return user
