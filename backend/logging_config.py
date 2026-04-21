"""Strukturerad JSON-loggning med structlog."""

import logging

import structlog

from backend.config import settings


def setup_logging() -> None:
    """Konfigurera structlog med JSON-output (console i DEBUG-läge)."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
            if settings.DEBUG
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
