"""Smoke-test som verifierar att grundläggande infrastruktur fungerar."""

from sqlmodel.ext.asyncio.session import AsyncSession


async def test_session_fixture_ger_async_session(session: AsyncSession) -> None:
    assert isinstance(session, AsyncSession)


def test_app_kan_importeras() -> None:
    from backend.api import app

    assert app.title
