from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime, timezone
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository
from database.models.tariff import Tariff


class TariffRepository(AsyncSQLAlchemyRepository[Tariff]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Tariff)

    async def get_by_name(self, name: str) -> Optional[Tariff]:
        stmt = select(self.model).where(self.model.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_tariffs(self) -> List[Tariff]:
        stmt = select(self.model).where(self.model.is_active)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_tariff_by_id(self, tariff_id: int) -> Optional[Tariff]:
        return await self.get(tariff_id)

    async def create_tariff(
        self,
        name: str,
        price: float,
        duration_days: int,
        description: str = None,
        features: str = None
    ) -> Tariff:
        tariff = Tariff(
            name=name,
            description=description,
            price=price,
            duration_days=duration_days,
            features=features,
            is_active=True
        )
        return await self.add(tariff)

    async def deactivate_tariff(self, tariff_id: int) -> Optional[Tariff]:
        tariff = await self.get(tariff_id)
        if tariff:
            tariff.is_active = False
            tariff.updated_at = datetime.now(timezone.utc)
            return await self.update(tariff)
        return None

    async def activate_tariff(self, tariff_id: int) -> Optional[Tariff]:
        tariff = await self.get(tariff_id)
        if tariff:
            tariff.is_active = True
            tariff.updated_at = datetime.now(timezone.utc)
            return await self.update(tariff)
        return None