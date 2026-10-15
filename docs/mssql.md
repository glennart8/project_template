# MS SQL i stället för Postgres

Mallens standard är Postgres, som passar de flesta, mindre projekten. Större
projekt kan använda kommunens MS SQL: drift skapar en tom databas och sköter
backupen, vi bygger schemat med Alembic som vanligt.

| | Postgres (standard) | MS SQL |
|---|---|---|
| Databasen körs | I en container på appservern | På driftens SQL Server |
| Backup | **Projektet själv** | Drift |
| Passar | Små projekt, data som går att återskapa | Större projekt, data som måste bevaras |

Principen gäller oavsett motor: **samma motor i test som i drift.** Ett projekt
på MS SQL utvecklas och testas mot SQL Server i Docker, aldrig mot Postgres.

Byte av motor görs när projektet skapas. Stegen nedan är ett recept, inte
testade i mallen — Konstregistret kör en variant av dem i drift.

---

## 1. Beställ av drift

- En **tom databas**.
- Två **SQL-inloggningar**: en för migrationerna, som får ändra schemat, och en
  för appen, som bara läser och skriver (`db_datareader`, `db_datawriter`).
  Appen ska aldrig vara `db_owner`.
- **SQL-inloggning**, inte Windows-inloggning — Windows-inloggning från en
  Linux-container kräver Kerberos.
- Öppning i brandväggen från appservern till databasservern, port 1433.

Fråga en gång, och skriv in svaren här:

- **Collation.** Styr sortering av å, ä, ö — och med `CI` (case insensitive)
  räknas `HEPI02` och `hepi02` som samma värde, även i unika index.
- **Certifikat.** Med ett betrott certifikat ansluter appen med `Encrypt=yes`.
  Utan det krävs `TrustServerCertificate=yes`, som inte kontrollerar servern.
- **Version och backup:** vilken SQL Server-version, hur ofta backup tas och
  hur en återläsning beställs.

## 2. Ändra i mallen

**Drivrutin**, i `backend/`:

```bash
uv remove psycopg
uv add pyodbc
```

**`backend/Dockerfile`** — ODBC-drivrutinen, före `COPY pyproject.toml`:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg \
    && . /etc/os-release \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
       | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/$VERSION_ID/prod $VERSION_CODENAME main" \
       > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*
```

**`DATABASE_URL`**:

```
mssql+pyodbc://<inloggning>:<lösenord>@<server>:1433/<databas>?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes
```

**Två inloggningar.** Lägg till `MIGRATION_DATABASE_URL` i `config.py` och låt
`migrations/env.py` använda den:

```python
url = config.get_main_option("sqlalchemy.url") or settings.MIGRATION_DATABASE_URL
```

**`docker-compose.yml`** — byt `db` mot SQL Server (Developer edition, gratis för
utveckling och test):

```yaml
  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_PID: Developer
      MSSQL_SA_PASSWORD: "Utveckling!1"   # bara lokalt
    ports:
      - "127.0.0.1:1433:1433"
      - "[::1]:1433:1433"
    volumes:
      - mssqldata:/var/opt/mssql
```

SQL Server skapar ingen databas av sig själv. Skapa `app` en gång:

```bash
docker compose exec db /opt/mssql-tools18/bin/sqlcmd -C -U sa -P "Utveckling!1" -Q "CREATE DATABASE app"
```

**`docker-compose.prod.yml`** — ta bort tjänsten `db` och volymen `pgdata`. Sätt
`DATABASE_URL` och `MIGRATION_DATABASE_URL` i serverns `.env`.

**`tests/conftest.py`** — `_create_test_database()` ansluter till `master` i
stället för `postgres` och frågar `sys.databases` i stället för `pg_database`.

**`tests/test_smoke.py`** — `func.current_database()` heter `func.db_name()`.

## 3. Bra att veta

- SQL Server-imagen är omkring 1,5 GB, kräver minst 2 GB minne och finns bara
  för x86 — inte för Mac med Apple-processor.
- Har en tabell en trigger, vägrar SQL Server `OUTPUT`, som SQLAlchemy använder
  vid insert. Sätt då `__table_args__ = {"implicit_returning": False}` på
  modellen. Konstregistret beskriver felet i sin `docs/databas.md`.
- Drift tar backupen, men en **återläsning ska ändå ha provats** innan systemet
  tas i drift.
