"""HTTP. Tar emot anropet och lämnar över till servicen — ingen regel, ingen SQL."""

import uuid

from fastapi import APIRouter, Depends

from auth import get_current_user
from dependencies import CurrentUserDep, SessionDep
from schemas import NoteCreate, NotePublic
from services import notes as service

# Varje endpoint kräver inloggning.
router = APIRouter(prefix="/notes", tags=["notes"], dependencies=[Depends(get_current_user)])


@router.get("")
def list_notes(session: SessionDep) -> list[NotePublic]:
    return service.list_notes(session)


@router.get("/{note_id}")
def get_note(note_id: uuid.UUID, session: SessionDep) -> NotePublic:
    return service.get_note(session, note_id)


@router.post("", status_code=201)
def create_note(data: NoteCreate, session: SessionDep, user: CurrentUserDep) -> NotePublic:
    return service.create_note(session, user, data)
