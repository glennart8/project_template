"""Reglerna. Kastar Pythons inbyggda fel; core/exceptions.py gör dem till HTTP."""

import logging
import uuid

from sqlmodel import Session

from core.auth import CurrentUser
from modules.notes import repository
from modules.notes.models import Note
from modules.notes.schemas import NoteCreate, NotePublic

logger = logging.getLogger(__name__)


def create_note(session: Session, user: CurrentUser, data: NoteCreate) -> NotePublic:
    text = data.text.strip()
    if not text:
        raise ValueError("Anteckningen får inte vara tom.")

    note = repository.add(session, Note(text=text, created_by=user.username))
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
