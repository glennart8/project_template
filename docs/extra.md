# Extrafunktionalitet

Mallen innehåller det som krävs för att utveckla och driftsätta. Det här är
tillägg som gör vardagen tryggare. Inget av dem behövs för att systemet ska
fungera, men var och en kräver att någon förstår den och tar ansvar för den.

Ordningen är den rekommenderade.

1. [CI — tester vid varje push](#1-ci--tester-vid-varje-push)
2. [Loggar som överlever en driftsättning](#2-loggar-som-överlever-en-driftsättning)
3. [Hälsokontroll och övervakning med larm](#3-hälsokontroll-och-övervakning-med-larm)
4. [Rätt IP-adress i loggarna](#4-rätt-ip-adress-i-loggarna)
5. [https ända fram till servern](#5-https-ända-fram-till-servern)
6. [Mätvärden](#6-mätvärden)
7. [Central loggsamling](#7-central-loggsamling)

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

## 2. Loggar som överlever en driftsättning

**Ger:** loggarna finns kvar efter `docker compose up --build`. Utan det försvinner
de varje gång en container byggs om — alltså vid varje uppdatering — och det går
inte att felsöka något som hände före den senaste.

**När:** så fort systemet är i drift och någon kan behöva felsöka i efterhand.

**Gör så här:** låt Docker skriva till serverns journal i stället för till
containerns egen fil. I `docker-compose.prod.yml`, byt blocket överst:

```yaml
x-logging: &logging
  # Serverns journal: överlever att containern byggs om, och journalen
  # roterar själv.
  driver: journald
```

Läs loggarna som förut med `docker compose logs`, eller direkt ur journalen:

```bash
journalctl CONTAINER_NAME=<projekt>-backend-1 --since "1 hour ago"
```

**Ansvar:** hur länge journalen sparas styrs av `SystemMaxUse` i
`/etc/systemd/journald.conf` på servern. Bestäm det tillsammans med den som
ansvarar för servern.

---

## 3. Hälsokontroll och övervakning med larm

**Ger:** ett larm när systemet ligger nere, innan användarna hör av sig.

**När:** när systemet används på riktigt.

Två delar: appen ska kunna svara på om den mår bra, och något utanför ska fråga
den regelbundet.

**a) Låt `/api/health` kontrollera databasen.** Idag svarar den `ok` så fort
appen lever, även om databasen är nere.

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

`backend/routers/system.py`:

```python
@router.get("/health")
def health(session: SessionDep, response: Response) -> dict[str, str]:
    if not is_database_up(session):
        response.status_code = 503
        return {"status": "databasen svarar inte"}
    return {"status": "ok"}
```

`backend/Dockerfile`, före `CMD`, så att `docker compose ps` visar
`healthy` eller `unhealthy`:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"
```

**b) Låt något fråga och larma.** Enklast är
[Uptime Kuma](https://github.com/louislam/uptime-kuma): en container med
webbgränssnitt som anropar `/api/health` varje minut och larmar via e-post eller
Teams.

```bash
docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data \
  --name uptime-kuma louislam/uptime-kuma:1
```

⚠ Kör den på **en annan server** än systemet den övervakar. Går servern ner,
ska larmet inte gå ner med den.

**Ansvar:** någon tar emot larmen och vet vad som ska göras.

---

## 4. Rätt IP-adress i loggarna

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

## 5. https ända fram till servern

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

---

## 6. Mätvärden

**Ger:** diagram över antal anrop, svarstider och fel över tid. Svarar på frågor
som ett larm inte gör: blir systemet långsammare? Vilken endpoint felar mest?

**När:** när det finns frågor om prestanda eller användning som loggarna inte
besvarar.

**Gör så här:** appen exponerar `/api/metrics` med biblioteket
`prometheus-client`. Prometheus hämtar värdena regelbundet och Grafana visar
dem. Konstregistret har en fungerande uppsättning att utgå från: `metrics.py`
och tjänsterna `prometheus` och `grafana` i dess `docker-compose.yml`.
Bakgrund: `DOKUMENTATION/prometheus.md` och `DOKUMENTATION/grafana.md`.

⚠ `/api/metrics` ska inte nås utifrån. Lägg den bakom Caddy med en regel som
bara släpper in Prometheus, eller låt Prometheus hämta direkt från backend
inne i Docker-nätverket.

**Ansvar:** någon underhåller Prometheus, Grafana och dashboards.

---

## 7. Central loggsamling

**Ger:** alla systems loggar sökbara på ett ställe, med tid och filter, i
stället för `docker compose logs` på varje server.

**När:** när ni har flera system i drift och felsöker över dem.

**Gör så här:** Alloy samlar containrarnas loggar och skickar dem till Loki,
som Grafana söker i. Konstregistret har en fungerande uppsättning: tjänsterna
`alloy` och `loki` i dess `docker-compose.yml`. Bakgrund:
`DOKUMENTATION/loki.md`.

**Ansvar:** någon äger Loki-servern, lagringstiden och åtkomsten. Loggarna får
inte innehålla personuppgifter — det gäller dubbelt när de samlas på ett ställe.
