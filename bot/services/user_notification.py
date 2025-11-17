from typing import Union, List
from schemas.user_notification import UserNotificationCreate, UserNotificationResponse, UserNotificationUpdate
from database.repositories.user_notification_repo import UserNotificationRepository
from database.repositories.notification_type_repo import NotificationTypeRepository
from database.models.user_notification import UserNotification

class UserNotificationService:
    def __init__(self, user_notification_repo: UserNotificationRepository, notification_type_repo: NotificationTypeRepository):
        self.user_notification_repo = user_notification_repo
        self.notification_type_repo = notification_type_repo

    async def create_user_notification(self, user_notification_data: UserNotificationCreate) -> Union[UserNotificationResponse, None]:
        notification_type = await self.notification_type_repo.get(user_notification_data.notification_type_id)
        if not notification_type:
            return None

        existing = await self.user_notification_repo.get_by_user_id_and_type_id(
            user_notification_data.user_id, user_notification_data.notification_type_id
        )
        if existing:
            for field, value in user_notification_data.model_dump(exclude_unset=True).items():
                setattr(existing, field, value)
            updated = await self.user_notification_repo.update(existing)
            return UserNotificationResponse.model_validate(updated)

        user_notification = UserNotification(
            user_id=user_notification_data.user_id,
            notification_type_id=user_notification_data.notification_type_id,
            is_active=user_notification_data.is_active
        )
        created = await self.user_notification_repo.add(user_notification)
        return UserNotificationResponse.model_validate(created)

    async def get_user_notification(self, user_id: int, notification_type_id: int) -> Union[UserNotificationResponse, None]:
        user_notification = await self.user_notification_repo.get_by_user_id_and_type_id(user_id, notification_type_id)
        if user_notification:
            return UserNotificationResponse.model_validate(user_notification)
        return None
        
    async def get_user_notifications(self, user_id: int) -> List[UserNotificationResponse]:
        user_notifications = await self.user_notification_repo.get_by_user_id(user_id)
        return [UserNotificationResponse.model_validate(un) for un in user_notifications]

    async def get_active_user_notifications(self, user_id: int) -> List[UserNotificationResponse]:
        user_notifications = await self.user_notification_repo.get_active_by_user_id(user_id)
        return [UserNotificationResponse.model_validate(un) for un in user_notifications]

    async def get_active_notification_type_names(self, user_id: int) -> List[str]:
        return await self.user_notification_repo.get_active_notification_type_names_by_user_id(user_id)

    async def update_user_notification(self, user_id: int, notification_type_id: int, user_notification_data: UserNotificationUpdate) -> Union[UserNotificationResponse, None]:
        user_notification = await self.user_notification_repo.get_by_user_id_and_type_id(user_id, notification_type_id)
        if user_notification:
            for field, value in user_notification_data.model_dump(exclude_unset=True).items():
                setattr(user_notification, field, value)
            updated = await self.user_notification_repo.update(user_notification)
            return UserNotificationResponse.model_validate(updated)
        return None

    async def delete_user_notification(self, user_id: int, notification_type_id: int) -> bool:
        return await self.user_notification_repo.delete_by_user_id_and_type_id(user_id, notification_type_id)
