"""Reglerna. Kastar Pythons inbyggda fel; errors.py gör dem till HTTP."""

import logging
import uuid

from sqlmodel import Session

from auth import CurrentUser
from models import Note
from repositories import notes as repository
from schemas import NoteCreate, NotePublic

logger = logging.getLogger(__name__)

# Svaren byggs med NotePublic.model_validate(note): fälten heter likadant i
# tabell och schema, och schemat bestämmer vad som går ut. Hämtar ett svar data
# från flera tabeller, skriv konstruktorn för hand, som i HR-systemets services.


def create_note(session: Session, user: CurrentUser, data: NoteCreate) -> NotePublic:
    text = data.text.strip()
    if not text:
        raise ValueError("Anteckningen får inte vara tom.")

    note = repository.add(session, Note(text=text, created_by=user.username))
    # Före commit: efter commit glömmer SQLAlchemy objektets värden.
    response = NotePublic.model_validate(note)
    session.commit()  # servicen äger transaktionen
    # Id, aldrig innehållet: texten kan innehålla personuppgifter.
    logger.info("Anteckning %s skapad", response.id)
    return response


def get_note(session: Session, note_id: uuid.UUID) -> NotePublic:
    note = repository.get(session, note_id)
    if note is None:
        raise LookupError("Anteckningen finns inte.")
    return NotePublic.model_validate(note)


def list_notes(session: Session) -> list[NotePublic]:
    return [NotePublic.model_validate(note) for note in repository.list_all(session)]


def delete_note(session: Session, user: CurrentUser, note_id: uuid.UUID) -> None:
    if "admin" not in user.roles:
        raise PermissionError("Bara admin får ta bort anteckningar.")

    note = repository.get(session, note_id)
    if note is None:
        raise LookupError("Anteckningen finns inte.")
    repository.delete(session, note)
    session.commit()
    logger.info("Anteckning %s borttagen", note_id)
