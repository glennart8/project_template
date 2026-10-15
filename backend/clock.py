"""Klockan. Använd den här i stället för datetime.now() och date.today().

Tider lagras i UTC med tidszon; datum gäller svensk tid. ruff-regeln DTZ
fäller tider utan tidszon.
"""

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

STOCKHOLM = ZoneInfo("Europe/Stockholm")


def now() -> datetime:
    return datetime.now(UTC)


def today() -> date:
    """Dagens datum i Sverige — inte i UTC, som kan vara gårdagen efter midnatt."""
    return datetime.now(STOCKHOLM).date()
