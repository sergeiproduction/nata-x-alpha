from typing import Union, List
from schemas.user_checklist_item import UserChecklistItemCreate, UserChecklistItemResponse, UserChecklistItemUpdate
from database.repositories.user_checklist_item_repo import UserChecklistItemRepository
from database.repositories.user_repo import UserRepository
from database.repositories.checklist_item_repo import ChecklistItemRepository
from database.models.user_checklist_item import UserChecklistItem

class UserChecklistItemService:
    def __init__(self, user_checklist_item_repo: UserChecklistItemRepository, user_repo: UserRepository, checklist_item_repo: ChecklistItemRepository):
        self.user_checklist_item_repo = user_checklist_item_repo
        self.user_repo = user_repo
        self.checklist_item_repo = checklist_item_repo

    async def create_user_checklist_item(self, user_checklist_item_data: UserChecklistItemCreate) -> Union[UserChecklistItemResponse, None]:
        user = await self.user_repo.get(user_checklist_item_data.user_id)
        if not user:
            return None

        item = await self.checklist_item_repo.get(user_checklist_item_data.item_id)
        if not item:
            return None

        existing = await self.user_checklist_item_repo.get_by_user_id_and_item_id(
            user_checklist_item_data.user_id, user_checklist_item_data.item_id
        )
        if existing:
            for field, value in user_checklist_item_data.model_dump(exclude_unset=True).items():
                setattr(existing, field, value)
            updated = await self.user_checklist_item_repo.update(existing)
            return UserChecklistItemResponse.model_validate(updated)

        user_checklist_item = UserChecklistItem(
            user_id=user_checklist_item_data.user_id,
            item_id=user_checklist_item_data.item_id,
            is_completed=user_checklist_item_data.is_completed
        )
        created = await self.user_checklist_item_repo.add(user_checklist_item)
        return UserChecklistItemResponse.model_validate(created)

    async def create_user_checklist_with_items(self, user_id: int, checklist_id: int, is_completed: bool = False) -> bool:
        """
        Создает чек-лист с элементами для пользователя, пропуская уже существующие
        """
        user = await self.user_repo.get(user_id)
        if not user:
            return False

        # Получаем все элементы чек-листа
        checklist_items = await self.checklist_item_repo.get_by_checklist_id(checklist_id)
        if not checklist_items:
            return False

        # Получаем уже существующие элементы чек-листа для пользователя
        existing_items = await self.user_checklist_item_repo.get_by_user_id(user_id, completed=None)
        existing_item_ids = {item.item_id for item in existing_items}

        # Создаем только те элементы, которых еще нет у пользователя
        user_checklist_items_to_create = []
        for checklist_item in checklist_items:
            if checklist_item.id not in existing_item_ids:
                user_checklist_item = UserChecklistItem(
                    user_id=user_id,
                    item_id=checklist_item.id,
                    is_completed=is_completed
                )
                user_checklist_items_to_create.append(user_checklist_item)

        if user_checklist_items_to_create:
            await self.user_checklist_item_repo.add_multiple(user_checklist_items_to_create)
        
        return True

    async def get_user_checklist_item(self, user_id: int, item_id: int) -> Union[UserChecklistItemResponse, None]:
        user_checklist_item = await self.user_checklist_item_repo.get_by_user_id_and_item_id(user_id, item_id)
        if user_checklist_item:
            return UserChecklistItemResponse.model_validate(user_checklist_item)
        return None

    async def get_user_checklist_items(self, user_id: int, completed: bool = None) -> List[UserChecklistItemResponse]:
        user_checklist_items = await self.user_checklist_item_repo.get_by_user_id(user_id, completed)
        return [UserChecklistItemResponse.model_validate(uc) for uc in user_checklist_items]

    async def get_user_items_by_checklist(self, user_id: int, checklist_id: int) -> List[UserChecklistItemResponse]:
        user_checklist_items = await self.user_checklist_item_repo.get_user_items_with_content_by_checklist_id(user_id, checklist_id)
        return [UserChecklistItemResponse.model_validate(uc) for uc in user_checklist_items]

    async def update_user_checklist_item(self, user_id: int, item_id: int, user_checklist_item_data: UserChecklistItemUpdate) -> Union[UserChecklistItemResponse, None]:
        user_checklist_item = await self.user_checklist_item_repo.get_by_user_id_and_item_id(user_id, item_id)
        if user_checklist_item:
            for field, value in user_checklist_item_data.model_dump(exclude_unset=True).items():
                setattr(user_checklist_item, field, value)
            updated = await self.user_checklist_item_repo.update(user_checklist_item)
            return UserChecklistItemResponse.model_validate(updated)
        return None

    async def delete_user_checklist_item(self, user_id: int, item_id: int) -> bool:
        existing = await self.user_checklist_item_repo.get_by_user_id_and_item_id(user_id, item_id)
        if existing:
            return await self.user_checklist_item_repo.delete(existing.id)
        return False

    async def delete_completed_user_items_by_checklist(self, user_id: int, checklist_id: int) -> int:
        return await self.user_checklist_item_repo.delete_completed_by_user_id_and_checklist_id(user_id, checklist_id)
