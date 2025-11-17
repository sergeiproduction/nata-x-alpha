from typing import List, Union
from schemas.checklist import ChecklistCreate, ChecklistResponse, ChecklistUpdate
from database.repositories.checklist_repo import ChecklistRepository
from database.models.checklist import Checklist

class ChecklistService:
    def __init__(self, checklist_repo: ChecklistRepository):
        self.checklist_repo = checklist_repo

    async def create_checklist(self, checklist_data: ChecklistCreate) -> ChecklistResponse:
        existing = await self.checklist_repo.get_by_name(checklist_data.name)
        if existing:
            return ChecklistResponse.model_validate(existing)

        checklist = Checklist(
            name=checklist_data.name,
            description=checklist_data.description,
            is_active=checklist_data.is_active
        )
        created = await self.checklist_repo.add(checklist)
        return ChecklistResponse.model_validate(created)

    async def get_checklist(self, id: int) -> Union[ChecklistResponse, None]:
        checklist = await self.checklist_repo.get(id)
        if checklist:
            return ChecklistResponse.model_validate(checklist)
        return None

    async def get_checklist_by_name(self, name: str) -> Union[ChecklistResponse, None]:
        checklist = await self.checklist_repo.get_by_name(name)
        if checklist:
            return ChecklistResponse.model_validate(checklist)
        return None

    async def list_checklists(self) -> List[ChecklistResponse]:
        checklists = await self.checklist_repo.list()
        return [ChecklistResponse.model_validate(c) for c in checklists]

    async def get_active_checklists(self) -> List[ChecklistResponse]:
        checklists = await self.checklist_repo.get_active_checklists()
        return [ChecklistResponse.model_validate(c) for c in checklists]

    async def update_checklist(self, id: int, checklist_data: ChecklistUpdate) -> Union[ChecklistResponse, None]:
        checklist = await self.checklist_repo.get(id)
        if checklist:
            for field, value in checklist_data.model_dump(exclude_unset=True).items():
                setattr(checklist, field, value)
            updated = await self.checklist_repo.update(checklist)
            return ChecklistResponse.model_validate(updated)
        return None

    async def delete_checklist(self, id: int) -> bool:
        return await self.checklist_repo.delete(id)
