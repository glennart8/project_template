# Projektnamn

Ändra titeln ovan till projektets namn.

## Setup

```bash
# Backend
cd backend
uv venv
uv sync
cp ../.env.example ../.env  # Redigera med rätt värden

# Frontend
cd ../frontend
npm install
```

## Utveckling

```bash
# Backend (port 8000)
cd backend && uv run uvicorn backend.api:app --reload

# Frontend (port 5173)
cd frontend && npm run dev
```

## Test & Lint

```bash
cd backend
uv run pytest -v
uv run ruff check .
```
