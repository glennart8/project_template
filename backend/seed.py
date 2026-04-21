"""Testdata / initial seed för utveckling."""

import asyncio

from backend.database import create_db_and_tables


async def seed() -> None:
    """Skapa tabeller och lägg in testdata."""
    await create_db_and_tables()
    # Lägg till seed-data här


if __name__ == "__main__":
    asyncio.run(seed())
