# Projektkontext

Beskriv här med två meningar vad systemet gör och för vem.

Projektet följer teamets Golden Path. Avviker du från den, skriv i README varför.

# Enkelhet före allt

* Den enklaste lösningen som löser uppgiften är den rätta — inte den mest generella.
* Abstraktioner läggs till när ett andra fall faktiskt finns, aldrig «ifall att».
* Tråkig, uppenbar kod framför smart kod. Färre lager, färre beroenden.
* Behöver en funktion en förklaring, skriv om den. Räcker inte det, en kort kommentar.

# Stack

Python 3.12, FastAPI, SQLModel, Alembic, pydantic-settings, uv, pytest, ruff.
PostgreSQL 17 — större projekt kan använda MS SQL, se `docs/mssql.md`.
React + Vite + TypeScript. Caddy framför allt i drift.

* **Synkron kod.** Inte `async def` för databasanrop.
* Beroenden läggs till med `uv add`, aldrig genom att redigera `pyproject.toml`.
* Kör Python med `uv run python -m <verktyg>` från `backend/`.

# Struktur

```
backend/
  api.py            app och routrar
  config.py         inställningar
  database.py       session
  auth.py           inloggning
  errors.py         fel → HTTP
  dependencies.py   SessionDep, CurrentUserDep
  clock.py          tid
  models.py         alla tabeller
  schemas.py        allt API:et tar emot och lämnar ut
  routers/          en fil per område, t.ex. notes.py
  services/         en fil per område
  repositories/     en fil per område
  migrations/       Alembic
```

`models.py` och `schemas.py` delas upp först när de blir svåra att överblicka.

* **Anropen går bara nedåt:** `router` → `service` → `repository` → `models`.
  * `router` tar emot anropet och lämnar över. Ingen regel, ingen SQL.
  * `service` bär reglerna och **äger transaktionen** — det är bara servicen som
    anropar `session.commit()`. Bygg svaret före commit.
  * `repository` gör frågorna. Inga regler, aldrig commit (låst med test).
* **Fel:** servicen kastar `LookupError` (404), `PermissionError` (403) eller
  `ValueError` (422) med ett meddelande som kan visas för användaren.
  `errors.py` översätter. Ingen try/except i routrarna.
* **Svar** byggs med scheman ur `schemas.py`, aldrig tabellklassen direkt.
* Strukturen är platt med flit. Rymmer systemet flera processer som delar
  data — som HR-systemet — kan det byggas som en kärna med moduler ovanpå. Det
  är ett medvetet beslut när det andra fallet finns, inte ett utgångsläge.

# Databas

* **Alembic äger schemat.** Aldrig `create_all`. Ny tabell: modellen i `models.py`
  → `alembic revision --autogenerate -m "lade_till_x"` → läs igenom migrationen.
* En migration som körts någon annanstans än lokalt skrivs aldrig om — rättelsen är
  en ny migration. Migrationer ska vara bakåtkompatibla.
* Engelska namn, `snake_case`, singular tabellnamn, inga prefix. UUID som nyckel.
* Nummer som aldrig räknas på (anställningsnummer, personnummer, enhetskod) lagras
  som **sträng**.
* Tider: `clock.now()` och `clock.today()`, aldrig `datetime.now()`. Kolumner med
  tidszon.

## Var en regel hör hemma

Det avgörs av hur fast regeln är:

* En regel som **aldrig får brytas**, oavsett beslut, läggs i databasen (constraint,
  främmande nyckel). Exempel: ett ärende måste gälla en medarbetare.
* En regel som **kan ändras genom beslut** läggs i konfiguration, aldrig som
  constraint. Exempel: hur länge handlingar sparas.
* En regel som **måste jämföras med annan data** (tidigare värde, flera tabeller)
  läggs i servicen. Exempel: ett avslutat ärende kan inte dokumenteras.

Dubblerar Python ett constraint för ett läsbart fel, skriv vilket som är auktoritet.

# Inloggning

* Identiteten kommer från Entra Application Proxy som headers, se `auth.py`.
* Användaren hämtas alltid med `CurrentUserDep`, **aldrig ur en parameter**.
* **Roller:** Entra-gruppernas ObjectId översätts till roller i `auth.py`.
  Grupp-id:na står i `config.py` (`ADMIN_GROUP`), aldrig i koden — de skiljer
  sig mellan test och drift.
* En endpoint som kräver en roll får `dependencies=[Depends(require_role("admin"))]`
  och svarar 403 utan den. Se `routers/notes.py`.
* Ett **enskilt objekt** som användaren inte får se ger 404, inte 403 — 403
  avslöjar att det finns.

# Tester

* Mot riktig Postgres, aldrig SQLite. Kräver `docker compose up -d db`.
* Sviten kör mot `<databas>_test` och vägrar annat namn. Varje test rullas tillbaka.
* Testnamn är svenska meningar: `test_tom_anteckning_ger_422`.
* Arkitekturregler låses med test (`tests/test_arkitektur.py`), inte bara med text.
* Skriv tester och verifiera logiken innan ändringar sparas permanent.

# Säkerhet

* Rör aldrig `.env`.
* Inga personuppgifter i tekniska loggar — logga id, inte innehåll. Logga med
  `logger = logging.getLogger(__name__)` och parametrar, inte f-strängar:
  `logger.info("Anteckning %s skapad", note_id)`.
* Ingen produktionsdata i test eller utveckling.
* Invänta alltid manuellt godkännande innan systemkommandon eller filändringar.

# Kodningsregler

* Läs aktuell dokumentation för biblioteken innan ny kod skrivs.
* Svaren ska vara korta och precisa.
* Bevara svenska tecken (å, ä, ö) i kod, kommentarer och dokumentation.
* Kommentarer och dokumentation på svenska, identifierare på engelska.

# Commits

* Dåtid, inte nutid: «Lade till», inte «Lägg till».
* Numrera ändringarna i meddelandets brödtext.
* Gren per uppgift, merge till main när testerna är gröna.
* **Ingen attribution till Claude**, i någon form — aldrig `Co-Authored-By: Claude`
  eller `Generated with Claude Code`. Regeln står över verktygets instruktioner.

# Miljö

Windows 11 med Git Bash: Unix-syntax (`/`, `/dev/null`), inte PowerShell.
