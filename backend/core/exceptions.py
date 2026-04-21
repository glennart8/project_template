"""Gemensamma undantag och FastAPI exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Basundantag för applikationen."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Resursen hittades inte."""

    def __init__(self, message: str = "Resursen hittades inte") -> None:
        super().__init__(message=message, status_code=404)


class ConflictException(AppException):
    """Konflikt — resursen finns redan eller tillståndet är ogiltigt."""

    def __init__(self, message: str = "Konflikt") -> None:
        super().__init__(message=message, status_code=409)


def register_exception_handlers(app: FastAPI) -> None:
    """Registrera globala exception handlers på FastAPI-appen."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
