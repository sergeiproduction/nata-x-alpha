from typing import Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
from database.models.campaign import Campaign
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class CampaignRepository(AsyncSQLAlchemyRepository[Campaign]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Campaign)

    async def get_by_name(self, name: str) -> Union[Campaign, None]:
        stmt = select(Campaign).where(Campaign.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_campaigns(self) -> List[Campaign]:
        now = datetime.now(timezone.utc)
        stmt = select(Campaign).where(Campaign.start_date <= now, Campaign.end_date >= now)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_expired_campaigns(self) -> List[Campaign]:
        now = datetime.now(timezone.utc)
        stmt = select(Campaign).where(Campaign.end_date < now)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_upcoming_campaigns(self, days_ahead: int = 7) -> List[Campaign]:
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days_ahead)
        stmt = select(Campaign).where(Campaign.start_date > now, Campaign.start_date <= future)
        result = await self.session.execute(stmt)
        return result.scalars().all()