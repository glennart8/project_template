"""Det API:et tar emot och lämnar ut. Skilt från tabellen, så att en ny kolumn
inte syns i API:et av misstag."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class NoteCreate(SQLModel):
    # Indatans form kontrolleras här och ger 422. Samma gräns som kolumnen i
    # models.py — tabellen kontrollerar inte själv, utan databasen ger 500.
    text: str = Field(max_length=2000)


class NotePublic(SQLModel):
    id: uuid.UUID
    text: str
    created_by: str
    created_at: datetime
