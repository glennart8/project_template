"""Det API:et tar emot och lämnar ut. Skilt från tabellen, så att en ny kolumn
inte syns i API:et av misstag."""

import uuid
from datetime import datetime

from sqlmodel import SQLModel


class NoteCreate(SQLModel):
    text: str


class NotePublic(SQLModel):
    id: uuid.UUID
    text: str
    created_by: str
    created_at: datetime
