from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.notification_type import NotificationType
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class NotificationTypeRepository(AsyncSQLAlchemyRepository[NotificationType]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, NotificationType)

    async def get_by_name(self, name: str) -> Union[NotificationType, None]:
        stmt = select(NotificationType).where(NotificationType.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()