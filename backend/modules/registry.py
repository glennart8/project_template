"""Modulregistrering — registrera domänspecifika routers här."""

from fastapi import FastAPI


def register_modules(app: FastAPI) -> None:
    """Registrera alla modulers routers på appen."""
    # Exempel:
    # from backend.modules.example.routers import router as example_router
    # app.include_router(example_router, prefix="/api/example", tags=["example"])
    pass
