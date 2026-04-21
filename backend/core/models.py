"""Gemensamma databasmodeller och Pydantic-scheman."""

from datetime import datetime

from sqlmodel import SQLModel, Field


class TimestampMixin(SQLModel):
    """Mixin för created_at/updated_at-fält."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)
