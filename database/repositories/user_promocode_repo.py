from typing import Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.models.user_promocode import UserPromocode
from database.models.campaign import Campaign
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class UserPromocodeRepository(AsyncSQLAlchemyRepository[UserPromocode]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserPromocode)

    async def get_by_user_id(self, user_id: int) -> List[UserPromocode]:
        stmt = select(UserPromocode).where(UserPromocode.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_campaign_id(self, campaign_id: int) -> List[UserPromocode]:
        stmt = select(UserPromocode).where(UserPromocode.campaign_id == campaign_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_name(self, name: str) -> Union[UserPromocode, None]:
        stmt = select(UserPromocode).where(UserPromocode.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_promocodes_by_user_id(self, user_id: int) -> List[UserPromocode]:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        stmt = (
            select(UserPromocode)
            .join(Campaign, UserPromocode.campaign_id == Campaign.id)
            .where(
                UserPromocode.user_id == user_id,
                Campaign.start_date <= now,
                Campaign.end_date >= now
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_by_user_id_and_campaign_id(self, user_id: int, campaign_id: int) -> int:
        stmt = delete(UserPromocode).where(
            UserPromocode.user_id == user_id,
            UserPromocode.campaign_id == campaign_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_by_user_id_and_campaign_id(self, user_id: int, campaign_id: int) -> Union[UserPromocode, None]:
        stmt = select(UserPromocode).where(
            UserPromocode.user_id == user_id,
            UserPromocode.campaign_id == campaign_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()