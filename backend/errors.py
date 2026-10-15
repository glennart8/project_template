"""Översätter servicelagrets fel till HTTP, på ett ställe.

Servicen kastar Pythons inbyggda fel med ett meddelande som kan visas för
användaren. Routrarna behöver då ingen try/except.
"""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

STATUS_BY_ERROR: dict[type[Exception], int] = {
    LookupError: 404,  # finns inte, eller får inte ses — 404 avslöjar inget
    PermissionError: 403,
    ValueError: 422,  # bryter mot en regel
}


def register_exception_handlers(app: FastAPI) -> None:
    """En hanterare per feltyp i STATUS_BY_ERROR."""
    for error, status in STATUS_BY_ERROR.items():
        app.add_exception_handler(error, _handler(status))


def _handler(status: int) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def handle(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    return handle
