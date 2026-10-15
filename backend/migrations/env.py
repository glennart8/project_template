"""Alembic kör migrationerna mot databasen i DATABASE_URL.

Testriggen sätter sqlalchemy.url själv, så att sviten migrerar testdatabasen.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlmodel import SQLModel

# Importera varje models-modul här, annars ser autogenerate inte tabellerna.
import modules.notes.models  # noqa: F401
from config import settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
engine = create_engine(url, poolclass=pool.NullPool)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=SQLModel.metadata)
    with context.begin_transaction():
        context.run_migrations()
