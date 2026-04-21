"""Gemensamma databasmodeller och Pydantic-scheman."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin för created_at/updated_at-fält."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = Field(default=None)
