# Projektnamn

Byt titeln mot projektets namn och skriv två meningar om vad systemet gör.

Mallen följer teamets Golden Path: FastAPI, SQLModel, Postgres, React och Caddy,
med inloggning via Entra Application Proxy. Reglerna står i [CLAUDE.md](CLAUDE.md),
driften i [docs/drift.md](docs/drift.md). Det som går att lägga till när behovet
finns står i [docs/extra.md](docs/extra.md).

## Stack

| Del | Verktyg | Används till |
|---|---|---|
| Backend | Python 3.12, FastAPI | API:et: endpoints, validering av anrop, API-dokumentation |
| Databaskod | SQLModel | Tabeller och API-scheman som Python-klasser |
| Schemaändringar | Alembic | Migrationer, en fil per ändring av databasen |
| Inställningar | pydantic-settings | Läser och kontrollerar `.env` och miljövariabler |
| Databas | PostgreSQL 17 | Standard. MS SQL i större projekt, se nedan. |
| Paket | uv, npm | Beroenden med låsfiler |
| Test och lint | pytest, ruff | Tester mot riktig databas, kodstil och vanliga fel |
| Frontend | React, TypeScript, Vite | Gränssnittet |
| Inloggning | Entra Application Proxy | Identiteten kommer som headers |
| Drift | Docker Compose, Caddy | Containrarna, och den enda vägen in |

**Databas:** Postgres passar de flesta projekt, men då sköter projektet själv
backupen. Större projekt kan använda kommunens MS SQL, där drift sköter backupen —
byt i så fall motor när projektet skapas, enligt [docs/mssql.md](docs/mssql.md).

## Prova direkt

Kräver bara Docker.

```bash
docker compose up -d --build      # http://localhost:8080
```

Du är inloggad som en testanvändare.

Kör du redan ett annat projekt från mallen krockar portarna 5432 och 8080. Stoppa
det andra (`docker compose stop` där), eller välj andra portar:
`DB_PORT=5433 WEB_PORT=8081 docker compose up -d --build`.

## Från mall till drift

1. **Skapa repot** från mallen (*Use this template*), i organisationens
   GitHub-konto. Byt namnet: `APP_NAME` i `backend/config.py` och `.env.example`,
   `<title>` i `frontend/index.html`, rubriken i `frontend/src/App.tsx` och den här
   README:n.
2. **Starta lokalt** (se nedan) och kontrollera att testerna är gröna.
3. **Bygg ditt första område** efter exemplet *notes*. I backend:
   `routers/notes.py`, `services/notes.py`, `repositories/notes.py`, `Note` i
   `models.py`, schemana i `schemas.py` och `tests/test_notes.py`. I frontend:
   typerna och anropen i `src/api.ts` och sidan i `src/App.tsx`.
   ⚠ **Skapa ingen migration ännu** — den skulle bygga vidare på exemplets.
4. **Ta bort exemplet:** filerna och klasserna ovan, raden i `api.py`, notes-delarna
   i `src/api.ts` och exemplets migration i `migrations/versions/`. Nollställ
   sedan databasen och skapa din första migration:

   ```bash
   docker compose down -v            # tömmer den lokala databasen
   docker compose up -d db
   cd backend
   uv run python -m alembic revision --autogenerate -m "lade_till_x"
   ```

5. **Kör testerna och pusha.**
6. **Driftsätt** enligt [docs/drift.md](docs/drift.md).

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
# Lägg till modellen i models.py, sedan:
cd backend
uv run python -m alembic revision --autogenerate -m "lade_till_x"
uv run python -m alembic upgrade head
```

Läs igenom den genererade migrationen innan den committas.
