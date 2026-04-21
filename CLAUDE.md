# Projektstandard & Arkitektur

Du agerar som en Senior Python Backend-utvecklare. All kod du genererar MÅSTE följa nedanstående branschstandarder för modern systemutveckling.

## 1. Teknisk Stack
* **Ramverk:** FastAPI
* **Databas & ORM:** SQLite + SQLModel
* **Pakethantering:** `uv`
* **Typsäkerhet:** Strict Type Hints, Pydantic, mypy.
* **Hantering av beroenden:** Använd uteslutande `uv add <paket>` för att installera eller uppdatera paket. Modifiera ALDRIG `pyproject.toml` manuellt.

## 2. Arkitektur (Separation of Concerns)
* Applikationen delas upp i tre skikt:
  1. **Router:** Hanterar endast HTTP, validering (Pydantic) och statuskoder. INGEN affärslogik eller databaskod.
  2. **Service:** Innehåller all affärslogik. Känner inte till HTTP.
  3. **Repository/Data:** Hanterar all interaktion med databasen (SQLModel).

* Mappstrukturen ska vara backend/core/ och backend/modules/

* **Dependency Injection:** Använd FastAPI:s `Depends()` för att injicera databassessioner och andra beroenden. Hårdkoda aldrig globala beroenden inuti funktioner.

## 3. Kodregler & Praxis
* **Konfiguration:** Använd ALDRIG `os.getenv()` i affärslogiken. All miljökonfiguration ska läsas in och valideras via `pydantic-settings` vid uppstart.
* **Asynkroni:** Använd `async def` och `await` för all I/O, inklusive databasanrop och externa requests.
* **DRY & SRP:** Funktioner ska göra en sak. Återanvänd logik, men undvik överabstraktion. Lite kodupprepning är bättre än hårt kopplad ("tight coupled") logik.

## 4. Test & Kvalitet
* **Testning:** Skriv tester i `pytest`. Använd fixtures och mocking för att isolera logik. Enhetstester får inte kräva en rullande server.
* **Linting:** Koden ska vara kompatibel med `ruff`.
* **Loggning:** Använd strukturerad JSON-loggning (t.ex. `structlog`), inte `print()`.

## 5. Kodningsregler och Beteende
* Läs alltid aktuell dokumentation för de specifika moduler och bibliotek som används innan ny kod genereras.
* Svaren ska vara korta och precisa.
* Använd modern och uppdaterad Python-standard (inklusive typ-hinting).
* Bevara alltid svenska tecken (å, ä, ö) i all kod, kommentarer och dokumentation. Ersätt ALDRIG med ASCII-motsvarigheter.
* Håll dokumentation och README:s enkla och koncisa.

## 6. Säkerhet
* Respektera `.claudeignore`. Rör aldrig `.env`, `*.joblib`, `*.db` eller annan känslig data.
* Utför exekvering inuti projektets virtuella miljö (`.venv`).
* Invänta alltid manuellt godkännande innan systemkommandon eller filändringar utförs.

## 7. Vid commits
* Använd dåtid, inte nutid.
* Numrera de ändringar som gjorts för tydlighet.
* Skriv aldrig med 'Co-Authored-By: Claude'
* Inkludera ALLA ändrade filer i commits om inte annat uttryckligen anges.

## 8. Miljö
* **OS:** Windows 11 (bash-shell via Git Bash)
* **Databas:** SQLite (detta projekt)
* **Frontend:** React/TypeScript
* **OBS:** Använd Unix-syntax (forward slashes, /dev/null) — inte PowerShell-syntax.
