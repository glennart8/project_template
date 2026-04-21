# Backend-koncept — vardagsnära förklaringar

En genomgång av de centrala byggstenarna i `backend/api.py`, `backend/database.py` och `backend/core/repositories/base.py`. Tanken är att jag ska förstå *varför* de finns, inte bara *vad* de heter.

---

## 1. `@asynccontextmanager`

**Vardagsbild:** tänk dig en bio. Innan filmen börjar tänds strålkastaren, dörrarna låses, och ljuset släcks. Efter filmen öppnas dörrarna och ljuset tänds igen. Själva filmen visas *mellan* dessa två steg.

En "context manager" är exakt det mönstret i kod: **gör något före**, **kör huvudlogiken**, **städa upp efter** — även om något går fel mitt i.

`@asynccontextmanager` är samma sak, fast för `async`-kod (kod som kan pausa och vänta på I/O).

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()              # initierar loggningssystemet vid uppstart
    await create_db_and_tables() # skapar databastabeller om de saknas
    yield                        # lämnar kontrollen till FastAPI; servern hanterar requests här
    # kod efter yield körs vid shutdown (t.ex. stäng anslutningar)
```

`yield` är "pausen" där kontrollen lämnas tillbaka till FastAPI. När servern stängs ned återupptas funktionen efter `yield`.

### Men — skapas tabellerna varje gång servern startar?

Rimlig fråga. `create_db_and_tables` i [backend/database.py:20-23](backend/database.py#L20-L23) anropas varje gång, men den översätts till SQL-satser med `CREATE TABLE IF NOT EXISTS`. Det innebär:

- **Första starten:** tabellerna finns inte → de skapas.
- **Alla följande starter:** tabellerna finns redan → SQLite svarar "ok, gör inget" på några millisekunder.

Operationen är *idempotent* — säker att köra om och om igen utan sidoeffekter.

### Haken med `create_all`

Den hanterar bara *nya* tabeller. Den:

- ✅ Skapar tabeller som saknas
- ❌ Lägger **inte** till nya kolumner i befintliga tabeller
- ❌ Ändrar **inte** kolumner som bytt typ eller namn
- ❌ Tar **inte** bort kolumner som tagits bort

Lägger du t.ex. till `email: str` på en redan existerande `User`-modell, händer ingenting i databasen vid omstart. Vid nästa INSERT får du antingen ett fel eller tyst skumt beteende.

### Produktionsvägen: Alembic

För riktiga projekt används ett migrationsverktyg — i Python-världen vanligtvis **Alembic** (byggt ihop med SQLAlchemy/SQLModel). Flödet blir:

1. Ändra modellen i Python.
2. `alembic revision --autogenerate` → genererar en migrationsfil med SQL-ändringarna.
3. `alembic upgrade head` → applicerar ändringarna på databasen.

`create_all` är rätt val för utveckling och prototyper där du kan slänga `app.db` och börja om. För produktion med riktig data är Alembic standard.

---

## 2. `lifespan(app: FastAPI)`

**Vardagsbild:** en affär har öppningsrutiner (tända skyltar, starta kassasystem) och stängningsrutiner (räkna kassan, släcka). `lifespan` är affärens öppnings-/stängningschecklista.

FastAPI säger: "Ge mig en funktion som jag kör *en gång vid start* och *en gång vid avslut*." Det är exakt där du lägger saker som:

- Starta loggning
- Skapa databastabeller
- Öppna anslutningar till externa tjänster
- Stänga samma anslutningar snyggt när servern går ner

```python
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,   # funktionen körs vid server-start och -stopp
)
```

Det gamla sättet var `@app.on_event("startup")` och `@app.on_event("shutdown")`. De är deprecated — `lifespan` är dagens standard.

---

## 3. `app.add_middleware()` och `CORSMiddleware`

**Vardagsbild:** en middleware är som en receptionist i entrén. Varje besökare (request) passerar receptionen innan de släpps in, och samma receptionist stämplar dem när de går ut (response). Receptionen kan *ändra*, *blockera*, eller *logga* det som passerar.

`add_middleware` säger: "Lägg till en receptionist av denna typ."

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Vad gör `CORSMiddleware`?

`CORS` = **Cross-Origin Resource Sharing**. Webbläsare har en säkerhetsregel: en sida som körs på `http://localhost:5173` får **inte** automatiskt anropa ett API på `http://localhost:8000`. De är olika "origins".

`CORSMiddleware` lägger till HTTP-headers som talar om för webbläsaren: "jodå, den här sidan får prata med mig". Utan den skulle din React-frontend få felet *"blocked by CORS policy"* när den försöker anropa backenden.

---

## 4. `CORS_ORIGINS`

**Vardagsbild:** gästlistan till dörrvakten. Bara de som står på listan släpps in.

```python
CORS_ORIGINS: list[str] = ["http://localhost:5173"]
```

Det betyder: "endast frontend som körs på port 5173 (Vites dev-server) får anropa detta API". I produktion lägger du till t.ex. `"https://app.minsajt.se"`.

**Varning:** `["*"]` släpper in *alla* — bekvämt i utveckling, osäkert i produktion.

---

## 5. `create_async_engine`

**Vardagsbild:** motorn i en bil. Den kör inte någonstans själv, men *allt* som har med databasen att göra går genom den. Den hanterar anslutningar, poolning (återanvändning av öppna anslutningar), och översättning mellan Python och SQL.

```python
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
```

- `settings.DATABASE_URL`: t.ex. `"sqlite+aiosqlite:///./app.db"` — vilken databas + vilken driver.
- `echo=True`: skriver ut varje SQL-query i loggen. Guldvärd vid felsökning, brusig i produktion.
- `async_`: den här motorn kan "pausa och vänta" på databasen utan att blockera resten av servern.

Du skapar engine **en gång** vid start och återanvänder den under hela serverns livstid.

---

## 6. `AsyncGenerator`

**Vardagsbild:** en PEZ-automat som levererar godis *en i taget, på begäran*, istället för att ge dig hela asken. En generator ger ut värden ett i taget via `yield`. "Async" betyder att den kan vänta mellan utdelningarna.

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session   # returnerar sessionen till den route som anropade beroendet
        # när routen är klar återupptas koden här och session stängs via async with
```

Typen `AsyncGenerator[AsyncSession, None]` betyder: "ger ut `AsyncSession`-objekt, tar inte emot något tillbaka".

FastAPI älskar detta mönster — det ger "setup + yield + cleanup" i samma funktion, perfekt för databassessioner.

---

## 7. `async_sessionmaker`

**Vardagsbild:** en kakform. Formen i sig är inte en kaka — den är en *mall* för att göra kakor. `async_sessionmaker` är en fabrik som tillverkar nya sessioner på beställning, alla konfigurerade likadant.

```python
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

Varje HTTP-request får en *egen* färsk session via `async_session_factory()`. Sessioner delas aldrig mellan requests — det skulle leda till trassel med transaktioner.

- `expire_on_commit=False`: efter `commit()` går objekten fortfarande att använda utan att behöva läsas om från databasen. Viktigt för async, annars kan du få oväntade fel.

---

## 8. `await` och `asyncio`

**Vardagsbild:** en kock som gör flera rätter samtidigt. När pastan kokar (10 minuter) *står inte kocken och stirrar* — hen förbereder såsen under tiden. När timern ringer går kocken tillbaka till pastan.

- `asyncio` är Pythons motor för att låta en enda tråd hantera många uppgifter genom att *växla* mellan dem när en är upptagen med att vänta (på disk, nätverk, databas).
- `await` är kockens "timer" — "starta detta, men låt mig göra annat under tiden, väck mig när det är klart".

```python
async def get_all(self) -> list[T]:
    result = await self.session.exec(select(self.model))
    #        ^^^^^ pausar funktionen tills databasen svarar; event-loopen kör annat under tiden
    return list(result.all())
```

**Regel:** `await` kan bara användas inuti `async def`. All I/O i projektet (databas, externa HTTP-anrop) ska vara `await`-bara — annars fryser hela servern medan den väntar.

---

## 9. `T = TypeVar`

**Vardagsbild:** bokstaven "X" i ett matteproblem. När du skriver `2x + 3`, så är `x` en platshållare — vilken siffra som helst kan stoppas in. `TypeVar` är samma sak, fast för *typer* istället för värden.

```python
from typing import Generic, TypeVar
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self.model = model

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)
```

Vad händer här?

- `T = TypeVar("T", bound=SQLModel)`: "T är en platshållare för *någon* typ, men den måste ärva från `SQLModel`".
- `Generic[T]`: "denna klass är generisk över T".
- När du sen skriver `BaseRepository[User]`, så "fylls T i" med `User` överallt. Då vet mypy och din IDE att `get_by_id` returnerar `User | None`, inte bara `SQLModel | None`.

**Vinsten:** en *enda* BaseRepository-klass fungerar för alla tabeller, och typkontrollen fungerar ändå perfekt. Utan `TypeVar` hade du behövt skriva samma CRUD-klass för varje modell — eller förlora typsäkerheten.

---

## Hur allt hänger ihop

```
Start av server
   │
   ▼
lifespan() kör — setup_logging(), create_db_and_tables()
   │
   ▼
FastAPI öppnar för requests
   │
   ▼
Varje request → CORSMiddleware → router → Depends(get_session)
                                              │
                                              ▼
                                    async_session_factory() ger en
                                    ny AsyncSession (via engine)
                                              │
                                              ▼
                                    BaseRepository[T] använder sessionen
                                    för att prata med databasen (await)
                                              │
                                              ▼
                                    session städas upp (AsyncGenerator)
   │
   ▼
Shutdown → lifespan fortsätter efter yield → städning
```

Alla bitarna är byggda för att:

1. **Inte blockera** (async hela vägen)
2. **Isolera state per request** (egen session varje gång)
3. **Vara typsäkra** (TypeVar + Generics)
4. **Ha tydliga livscykler** (lifespan + context managers)
