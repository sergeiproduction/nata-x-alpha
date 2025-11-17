from typing import List, Union
from schemas.notification_type import NotificationTypeCreate, NotificationTypeResponse, NotificationTypeUpdate
from database.repositories.notification_type_repo import NotificationTypeRepository
from database.models.notification_type import NotificationType

class NotificationTypeService:
    def __init__(self, notification_type_repo: NotificationTypeRepository):
        self.notification_type_repo = notification_type_repo

    async def create_notification_type(self, notification_type_data: NotificationTypeCreate) -> NotificationTypeResponse:
        existing = await self.notification_type_repo.get_by_name(notification_type_data.name)
        if existing:
            return NotificationTypeResponse.model_validate(existing)

        notification_type = NotificationType(
            name=notification_type_data.name,
            description=notification_type_data.description,
            default_enabled=notification_type_data.default_enabled,
            advance_days=notification_type_data.advance_days
        )
        created = await self.notification_type_repo.add(notification_type)
        return NotificationTypeResponse.model_validate(created)

    async def get_notification_type(self, id: int) -> Union[NotificationTypeResponse, None]:
        notification_type = await self.notification_type_repo.get(id)
        if notification_type:
            return NotificationTypeResponse.model_validate(notification_type)
        return None

    async def get_notification_type_by_name(self, name: str) -> Union[NotificationTypeResponse, None]:
        notification_type = await self.notification_type_repo.get_by_name(name)
        if notification_type:
            return NotificationTypeResponse.model_validate(notification_type)
        return None

    async def list_notification_types(self) -> List[NotificationTypeResponse]:
        notification_types = await self.notification_type_repo.list()
        return [NotificationTypeResponse.model_validate(nt) for nt in notification_types]

    async def update_notification_type(self, id: int, notification_type_data: NotificationTypeUpdate) -> Union[NotificationTypeResponse, None]:
        notification_type = await self.notification_type_repo.get(id)
        if notification_type:
            for field, value in notification_type_data.model_dump(exclude_unset=True).items():
                setattr(notification_type, field, value)
            updated = await self.notification_type_repo.update(notification_type)
            return NotificationTypeResponse.model_validate(updated)
        return None

    async def delete_notification_type(self, id: int) -> bool:
        return await self.notification_type_repo.delete(id)
