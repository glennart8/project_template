"""Tabellerna. Schemat i databasen ägs av Alembic — se migrations/versions/."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

import clock


class Note(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    text: str = Field(max_length=2000)
    # Användarnamnet ur inloggningen. Sträng, aldrig siffra: ledande nollor.
    created_by: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=clock.now, sa_type=DateTime(timezone=True))
