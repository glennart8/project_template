"""Alembic kör migrationerna mot databasen i DATABASE_URL.

Testriggen sätter sqlalchemy.url själv, så att sviten migrerar testdatabasen.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlmodel import SQLModel

# Tabellerna måste vara importerade, annars ser autogenerate dem inte.
import models  # noqa: F401
from config import settings

config = context.config
# Testriggen kör migrationerna i samma process som appen och stänger av detta:
# loggkonfigurationen i alembic.ini skulle annars tysta appens loggar.
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name)

url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
engine = create_engine(url, poolclass=pool.NullPool)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=SQLModel.metadata)
    with context.begin_transaction():
        context.run_migrations()
