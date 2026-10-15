"""Reglerna. Kastar Pythons inbyggda fel; errors.py gör dem till HTTP."""

import logging
import uuid

from sqlmodel import Session

from auth import CurrentUser
from models import Note
from repositories import notes as repository
from schemas import NoteCreate, NotePublic

logger = logging.getLogger(__name__)


def _to_public(note: Note) -> NotePublic:
    """Tabellraden → det API:et lämnar ut. Fälten skrivs ut, så att en ny kolumn
    inte hamnar i API:et av misstag."""
    return NotePublic(
        id=note.id,
        text=note.text,
        created_by=note.created_by,
        created_at=note.created_at,
    )


def create_note(session: Session, user: CurrentUser, data: NoteCreate) -> NotePublic:
    text = data.text.strip()
    if not text:
        raise ValueError("Anteckningen får inte vara tom.")

    note = repository.add(session, Note(text=text, created_by=user.username))
    # Före commit: efter commit glömmer SQLAlchemy objektets värden.
    response = _to_public(note)
    session.commit()  # servicen äger transaktionen
    # Id, aldrig innehållet: texten kan innehålla personuppgifter.
    logger.info("Anteckning %s skapad", response.id)
    return response


def get_note(session: Session, note_id: uuid.UUID) -> NotePublic:
    note = repository.get(session, note_id)
    if note is None:
        raise LookupError("Anteckningen finns inte.")
    return _to_public(note)


def list_notes(session: Session) -> list[NotePublic]:
    return [_to_public(note) for note in repository.list_all(session)]


def delete_note(session: Session, user: CurrentUser, note_id: uuid.UUID) -> None:
    if "admin" not in user.roles:
        raise PermissionError("Bara admin får ta bort anteckningar.")

    note = repository.get(session, note_id)
    if note is None:
        raise LookupError("Anteckningen finns inte.")
    repository.delete(session, note)
    session.commit()
    logger.info("Anteckning %s borttagen", note_id)
