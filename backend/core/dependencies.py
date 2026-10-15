"""Centrala FastAPI-beroenden för dependency injection."""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from database import get_session

SessionDep = Annotated[Session, Depends(get_session)]

__all__ = ["SessionDep", "get_session"]
