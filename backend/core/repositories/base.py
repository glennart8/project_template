"""Generisk bas-repository med CRUD-operationer."""

from typing import Any, Generic, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """Bas-repository med standardoperationer för CRUD."""

    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def get_all(self) -> list[T]:
        result = await self.session.exec(select(self.model))
        return list(result.all())

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: T, data: dict[str, Any]) -> T:
        """Partiell uppdatering via SQLModels sqlmodel_update."""
        obj.sqlmodel_update(data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        await self.session.delete(obj)
        await self.session.commit()
