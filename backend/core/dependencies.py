"""Centrala FastAPI-beroenden för dependency injection."""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from database import get_session

# Genom att definiera SessionDep här kan vi enkelt importera det i alla routers och
# få en AsyncSession via dependency injection.
SessionDep = Annotated[AsyncSession, Depends(get_session)]

__all__ = ["SessionDep", "get_session"]
