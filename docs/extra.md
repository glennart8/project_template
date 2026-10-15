# Extrafunktionalitet

Mallen innehåller det som krävs för att utveckla och driftsätta. Det här är
tillägg som gör vardagen tryggare. Inget av dem behövs för att systemet ska
fungera, men var och en kräver att någon förstår den och tar ansvar för den.

Ordningen är den rekommenderade.

---

## 1. CI — tester vid varje push

**Ger:** GitHub kör lint, tester mot Postgres, frontendbygget och driftens images
vid varje push till main. Ett test som faller syns innan koden når servern.

**När:** så fort mer än en person pushar till repot.

**Gör så här:** spara filen nedan som `.github/workflows/ci.yml`.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    # Testerna kräver riktig Postgres.
    services:
      db:
        image: postgres:17
        env:
          POSTGRES_USER: app
          POSTGRES_PASSWORD: app
          POSTGRES_DB: app
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U app -d app"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
    env:
      DATABASE_URL: postgresql+psycopg://app:app@localhost:5432/app
    steps:
      - uses: actions/checkout@v7
      # Exakt version: setup-uv publicerar ingen flyttbar huvudversionstagg.
      - uses: astral-sh/setup-uv@v10.3.0
      - name: Installera beroenden
        working-directory: backend
        run: uv sync --locked
      - name: Lint
        working-directory: backend
        run: uv run ruff check .
      - name: Tester
        working-directory: backend
        run: uv run pytest -v

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - name: Installera beroenden
        working-directory: frontend
        run: npm ci
      - name: Bygg
        working-directory: frontend
        run: npm run build

  # Fångar en trasig Dockerfile innan den når servern.
  images:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - name: Bygg driftens images
        run: POSTGRES_PASSWORD=ci docker compose -f docker-compose.prod.yml build
```

**Ansvar:** någon håller versionerna av actions aktuella. GitHub varnar i
körningens sammanfattning när en version blir föråldrad.

---

## 2. Hälsokontroll med databas

**Ger:** `/api/health` svarar 503 när databasen inte svarar, och Docker visar
`healthy` eller `unhealthy` i `docker compose ps`.

**När:** när något övervakar systemet och kan larma. Utan övervakning läser
ingen värdet.

**Gör så här:**

`backend/database.py`:

```python
from sqlalchemy import literal
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select


def is_database_up(session: Session) -> bool:
    """För hälsokontrollen: svarar databasen?"""
    try:
        session.exec(select(literal(1))).one()
    except SQLAlchemyError:
        return False
    return True
```

`backend/core/routers/system.py`:

```python
@router.get("/health")
def health(session: SessionDep, response: Response) -> dict[str, str]:
    if not is_database_up(session):
        response.status_code = 503
        return {"status": "databasen svarar inte"}
    return {"status": "ok"}
```

`backend/Dockerfile`, före `CMD`:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"
```

---

## 3. Rätt IP-adress i loggarna

**Ger:** backend ser användarens IP-adress i stället för Caddys.

**När:** när systemet loggar IP-adresser, till exempel i en auditlogg över vem
som läst vad.

**Gör så här:** lägg till flaggorna sist i `CMD` i `backend/Dockerfile`:

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn api:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]
```

`*` betyder att backend litar på alla avsändare. Det går bara för att backend
aldrig har en öppen port utanför Docker — bara Caddy når den.

---

## 4. https ända fram till servern

**Ger:** krypterad trafik även mellan App Proxy-connectorn och servern.

**När:** när informationssäkerheten kräver det. App Proxy krypterar redan
trafiken fram till kommunnätet.

**Gör så här:** byt `:80` i `frontend/Caddyfile` mot serverns namn och välj
certifikat:

```
minapp.udn.ds {
	tls internal          # Caddys egna certifikat
	...
}
```

Öppna port 443 i `docker-compose.prod.yml`. Med `tls internal` måste
connectorn lita på Caddys rotcertifikat; med kommunens certifikat pekar
`tls` på certifikatfilerna i stället.
