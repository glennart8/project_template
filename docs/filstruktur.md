project_root/
├── frontend/                       # React + TypeScript (Vite)
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf                  # Nginx-config för produktion
│   ├── src/
│   └── public/
│
├── backend/                        # Python-applikationen
│   ├── .venv/                      # Isolerad virtuell miljö
│   ├── pyproject.toml              # Beroenden (via uv)
│   ├── Dockerfile
│   ├── api.py                      # FastAPI-app, router-registrering, CORS
│   ├── config.py                   # pydantic-settings, miljövariabler
│   ├── database.py                 # Engine, sessionshantering
│   ├── logging_config.py           # Structlog-konfiguration
│   ├── seed.py                     # Testdata / initial seed
│   ├── assets/                     # Statiska filer (mallar, bilder, ikoner)
│   │
│   ├── core/                       # Delad generisk logik (ej domänspecifik)
│   │   ├── __init__.py
│   │   ├── models.py               # Gemensamma databasmodeller och Pydantic-scheman
│   │   ├── dependencies.py         # Centrala Depends()-injektioner
│   │   ├── exceptions.py           # Gemensamma undantag + exception handlers
│   │   ├── routers/                # Generiska endpoints
│   │   ├── services/               # Gemensam affärslogik
│   │   └── repositories/           # Gemensamma databasanrop + basklasser
│   │
│   ├── modules/                    # Domänspecifika moduler
│   │   ├── basemodels.py           # Delade basmodeller för moduler
│   │   ├── registry.py             # Modulregistrering
│   │   │
│   │   └── <modul>/               # Ex: alkoholtillstånd, bygglov
│   │       ├── __init__.py
│   │       ├── models.py           # Modulens databasmodeller
│   │       ├── schemas.py          # Modulens Pydantic-scheman
│   │       ├── module_config.py    # Modulspecifik konfiguration
│   │       ├── routers/            # Modulens endpoints
│   │       ├── services/           # Modulens affärslogik
│   │       └── repositories/       # Modulens databasanrop
│   │
│   └── tests/                      # Pytest-tester
│       ├── conftest.py             # Fixtures, test-databas
│       ├── core/                   # Tester för core
│       └── modules/                # Tester per modul
│
├── docs/                           # Dokumentation
├── docker-compose.yml              # Docker Compose för hela stacken
├── .gitignore
├── .claudeignore
├── .dockerignore
├── .env.example                    # Mall för miljövariabler
├── ruff.toml                       # Linting-konfiguration
├── CLAUDE.md                       # Projektstandard för hela monorepot
└── README.md
