from typing import Union, List
from schemas.checklist_item import ChecklistItemCreate, ChecklistItemResponse, ChecklistItemUpdate
from database.repositories.checklist_item_repo import ChecklistItemRepository
from database.repositories.checklist_repo import ChecklistRepository
from database.models.checklist_item import ChecklistItem

class ChecklistItemService:
    def __init__(self, checklist_item_repo: ChecklistItemRepository, checklist_repo: ChecklistRepository):
        self.checklist_item_repo = checklist_item_repo
        self.checklist_repo = checklist_repo

    async def create_checklist_item(self, checklist_item_data: ChecklistItemCreate) -> Union[ChecklistItemResponse, None]:
        # Проверим, существует ли чек-лист
        checklist = await self.checklist_repo.get(checklist_item_data.checklist_id)
        if not checklist:
            return None # Чек-лист не найден

        checklist_item = ChecklistItem(
            checklist_id=checklist_item_data.checklist_id,
            content=checklist_item_data.content
        )
        created = await self.checklist_item_repo.add(checklist_item)
        return ChecklistItemResponse.model_validate(created)

    async def get_checklist_item(self, id: int) -> Union[ChecklistItemResponse, None]:
        checklist_item = await self.checklist_item_repo.get(id)
        if checklist_item:
            return ChecklistItemResponse.model_validate(checklist_item)
        return None

    async def get_checklist_items(self, checklist_id: int) -> List[ChecklistItemResponse]:
        checklist_items = await self.checklist_item_repo.get_by_checklist_id(checklist_id)
        return [ChecklistItemResponse.model_validate(ci) for ci in checklist_items]

    async def update_checklist_item(self, id: int, checklist_item_data: ChecklistItemUpdate) -> Union[ChecklistItemResponse, None]:
        checklist_item = await self.checklist_item_repo.get(id)
        if checklist_item:
            for field, value in checklist_item_data.model_dump(exclude_unset=True).items():
                setattr(checklist_item, field, value)
            updated = await self.checklist_item_repo.update(checklist_item)
            return ChecklistItemResponse.model_validate(updated)
        return None

    async def delete_checklist_item(self, id: int) -> bool:
        return await self.checklist_item_repo.delete(id)

    async def delete_checklist_items_by_checklist_id(self, checklist_id: int) -> int:
        return await self.checklist_item_repo.delete_by_checklist_id(checklist_id)
