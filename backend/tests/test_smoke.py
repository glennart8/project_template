"""Smoke-test som verifierar att grundläggande infrastruktur fungerar."""

from sqlmodel.ext.asyncio.session import AsyncSession

from api import app


async def test_session_fixture_ger_async_session(session: AsyncSession) -> None:
    assert isinstance(session, AsyncSession)


def test_app_kan_importeras() -> None:
    assert app.title


def test_systemroutrar_ar_registrerade() -> None:
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/version" in paths
