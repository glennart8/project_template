"""Testdata / initial seed för utveckling."""

from database import create_db_and_tables


def seed() -> None:
    """Skapa tabeller och lägg in testdata."""
    create_db_and_tables()
    # Lägg till seed-data här


if __name__ == "__main__":
    seed()
