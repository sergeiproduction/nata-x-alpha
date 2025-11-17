from typing import Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.models.user_referral import UserReferral
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class UserReferralRepository(AsyncSQLAlchemyRepository[UserReferral]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserReferral)

    async def get_referrals_by_user_id(self, user_id: int) -> List[UserReferral]:
        stmt = select(UserReferral).where(UserReferral.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_referrer_by_referee_id(self, referrer_id: int) -> Union[UserReferral, None]:
        stmt = select(UserReferral).where(UserReferral.referrer_id == referrer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete_referral(self, user_id: int, referrer_id: int) -> bool:
        stmt = delete(UserReferral).where(UserReferral.user_id == user_id, UserReferral.referrer_id == referrer_id)
        result = await self.session.execute(stmt)
        deleted_count = result.rowcount
        return deleted_count > 0

    async def get_by_user_id_and_referrer_id(self, user_id: int, referrer_id: int) -> Union[UserReferral, None]:
        stmt = select(UserReferral).where(UserReferral.user_id == user_id, UserReferral.referrer_id == referrer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()