"""Testdata för utveckling. Kör efter `alembic upgrade head`."""

from sqlmodel import Session

from database import engine


def seed() -> None:
    """Lägg in testdata."""
    with Session(engine) as session:
        # session.add(...)
        session.commit()


if __name__ == "__main__":
    seed()
