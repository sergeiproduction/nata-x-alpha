from typing import  List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.models.checklist_item import ChecklistItem
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class ChecklistItemRepository(AsyncSQLAlchemyRepository[ChecklistItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChecklistItem)

    async def get_by_checklist_id(self, checklist_id: int) -> List[ChecklistItem]:
        stmt = select(ChecklistItem).where(ChecklistItem.checklist_id == checklist_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_by_checklist_id(self, checklist_id: int) -> int:
        stmt = delete(ChecklistItem).where(ChecklistItem.checklist_id == checklist_id)
        result = await self.session.execute(stmt)
        return result.rowcount