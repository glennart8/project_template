FROM python:3.12-slim

# Låst version, så att bygget blir likadant varje gång.
COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /usr/local/bin/uv

WORKDIR /app

# Beroendena först: lagret återanvänds så länge låsfilen är oförändrad.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY . .

# Containern körs inte som root.
RUN useradd --create-home app
USER app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

# Migrationerna körs vid varje start; Alembic hoppar över dem som redan körts.
CMD ["sh", "-c", "alembic upgrade head && uvicorn api:app --host 0.0.0.0 --port 8000"]
