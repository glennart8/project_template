"""Centrala FastAPI-beroenden för dependency injection."""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.database import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

__all__ = ["SessionDep", "get_session"]
