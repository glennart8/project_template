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
PostgreSQL 17. React + Vite + TypeScript. Caddy framför allt i drift.

* **Synkron kod.** Inte `async def` för databasanrop.
* Beroenden läggs till med `uv add`, aldrig genom att redigera `pyproject.toml`.
* Kör Python med `uv run python -m <verktyg>` från `backend/`.

# Struktur

```
backend/
  api.py, config.py, database.py, clock.py
  core/       det alla moduler delar: inloggning, felhantering, systemroutrar
  modules/    en katalog per område: router.py, service.py, repository.py,
              models.py, schemas.py — filerna skapas när de behövs
  migrations/ Alembic
```

* **Anropen går bara nedåt:** `router` → `service` → `repository` → `models`.
  * `router` tar emot anropet och lämnar över. Ingen regel, ingen SQL.
  * `service` bär reglerna och **äger transaktionen** — det är bara servicen som
    anropar `session.commit()`. Bygg svaret före commit.
  * `repository` gör frågorna. Inga regler, aldrig commit (låst med test).
* **Fel:** servicen kastar `LookupError` (404), `PermissionError` (403) eller
  `ValueError` (422) med ett meddelande som kan visas för användaren.
  `core/exceptions.py` översätter. Ingen try/except i routrarna.
* **Svar** byggs med scheman ur `schemas.py`, aldrig tabellklassen direkt.
* En modul beror bara på `core`, aldrig på en annan modul.

# Databas

* **Alembic äger schemat.** Aldrig `create_all`. Ny tabell: modell → importera i
  `migrations/env.py` → `alembic revision --autogenerate -m "lade_till_x"`.
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

* Identiteten kommer från Entra Application Proxy som headers, se `core/auth.py`.
* Användaren hämtas alltid med `CurrentUserDep`, **aldrig ur en parameter**.
* Vad användaren får göra avgör appen utifrån gruppernas ObjectId.
* Den som inte får se något får 404, inte 403 — 403 avslöjar att det finns.

# Tester

* Mot riktig Postgres, aldrig SQLite. Kräver `docker compose up -d db`.
* Sviten kör mot `<databas>_test` och vägrar annat namn. Varje test rullas tillbaka.
* Testnamn är svenska meningar: `test_tom_anteckning_ger_422`.
* Arkitekturregler låses med test (`tests/test_arkitektur.py`), inte bara med text.
* Skriv tester och verifiera logiken innan ändringar sparas permanent.

# Säkerhet

* Rör aldrig `.env`.
* Inga personuppgifter i tekniska loggar — logga id, inte innehåll.
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
