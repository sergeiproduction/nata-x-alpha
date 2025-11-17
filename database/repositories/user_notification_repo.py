from typing import Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.models.user_notification import UserNotification
from database.models.notification_type import NotificationType
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class UserNotificationRepository(AsyncSQLAlchemyRepository[UserNotification]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserNotification)

    async def get_by_user_id(self, user_id: int) -> List[UserNotification]:
        stmt = select(UserNotification).where(UserNotification.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id_and_type_id(self, user_id: int, notification_type_id: int) -> Union[UserNotification, None]:
        stmt = select(UserNotification).where(
            UserNotification.user_id == user_id,
            UserNotification.notification_type_id == notification_type_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_user_id(self, user_id: int) -> List[UserNotification]:
        stmt = select(UserNotification).where(
            UserNotification.user_id == user_id,
            UserNotification.is_active
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active_notification_type_names_by_user_id(self, user_id: int) -> List[str]:
        stmt = (
            select(NotificationType.name)
            .join(UserNotification, NotificationType.id == UserNotification.notification_type_id)
            .where(UserNotification.user_id == user_id, UserNotification.is_active)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_by_user_id_and_type_id(self, user_id: int, notification_type_id: int) -> bool:
        stmt = delete(UserNotification).where(
            UserNotification.user_id == user_id,
            UserNotification.notification_type_id == notification_type_id
        )
        result = await self.session.execute(stmt)
        deleted_count = result.rowcount
        return deleted_count > 0
