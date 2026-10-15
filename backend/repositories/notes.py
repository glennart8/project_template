"""Databasfrågorna. Inga regler, och aldrig commit — det gör servicen."""

import uuid

from sqlmodel import Session, select

from models import Note


def add(session: Session, note: Note) -> Note:
    session.add(note)
    session.flush()  # skickar raden nu, så att databasfel syns här och inte vid commit
    return note


def get(session: Session, note_id: uuid.UUID) -> Note | None:
    return session.get(Note, note_id)


def list_all(session: Session) -> list[Note]:
    return list(session.exec(select(Note).order_by(Note.created_at.desc())))


def delete(session: Session, note: Note) -> None:
    session.delete(note)
    session.flush()
