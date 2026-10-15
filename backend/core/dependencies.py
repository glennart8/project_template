"""Centrala FastAPI-beroenden för dependency injection."""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from core.auth import CurrentUser, get_current_user
from database import get_session

SessionDep = Annotated[Session, Depends(get_session)]
# Användaren hämtas alltid ur inloggningen, aldrig ur en parameter i anropet.
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]

__all__ = ["CurrentUserDep", "SessionDep", "get_session"]
