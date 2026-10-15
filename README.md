# Projektnamn

Byt titeln mot projektets namn och skriv två meningar om vad systemet gör.

Mallen följer teamets Golden Path: FastAPI, SQLModel, Postgres, React och Caddy,
med inloggning via Entra Application Proxy. Reglerna står i [CLAUDE.md](CLAUDE.md),
driften i [docs/drift.md](docs/drift.md). Det som går att lägga till när behovet
finns står i [docs/extra.md](docs/extra.md).

## Prova direkt

Kräver bara Docker.

```bash
docker compose up -d --build      # http://localhost:8080
```

Du är inloggad som en testanvändare.

## Från mall till drift

1. **Skapa repot** från mallen, i organisationens GitHub-konto. Byt `APP_NAME`,
   titeln i `frontend/index.html` och den här README:n.
2. **Starta lokalt** (se nedan) och kontrollera att testerna är gröna.
3. **Bygg din första modul** efter exemplet i `backend/modules/notes/`. Ta sedan bort
   exemplet: katalogen, raden i `api.py`, importen i `migrations/env.py`, dess
   migration och `tests/test_notes.py`.
4. **Kör testerna och pusha.**
5. **Driftsätt** enligt [docs/drift.md](docs/drift.md).

## Utveckla lokalt

Med omladdning när du sparar. Kräver Docker, [uv](https://docs.astral.sh/uv/) och
Node 22.

```bash
cp .env.example .env              # mock-inloggning, lokal databas
docker compose up -d db           # Postgres på localhost:5432

cd backend
uv sync
uv run python -m alembic upgrade head
uv run python -m uvicorn api:app --reload     # http://localhost:8000/api/docs

cd ../frontend
npm ci
npm run dev                                   # http://localhost:5173
```

## Test och lint

```bash
cd backend
uv run python -m pytest
uv run python -m ruff check .
```

Testerna kör mot en egen databas, `app_test`, som skapas och migreras automatiskt.

## Ny tabell

```bash
# 1. Modellen i modules/<område>/models.py
# 2. Importera modulen i migrations/env.py
cd backend
uv run python -m alembic revision --autogenerate -m "lade_till_x"
uv run python -m alembic upgrade head
```

Läs igenom den genererade migrationen innan den committas.
