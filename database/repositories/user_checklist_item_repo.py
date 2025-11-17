from typing import Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.models.user_checklist_item import UserChecklistItem
from database.models.checklist_item import ChecklistItem
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class UserChecklistItemRepository(AsyncSQLAlchemyRepository[UserChecklistItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserChecklistItem)


    async def add_multiple(self, user_checklist_items: List[UserChecklistItem]) -> List[UserChecklistItem]:
            """Добавляет несколько записей за один запрос"""
            self.session.add_all(user_checklist_items)
            await self.session.commit()
            for item in user_checklist_items:
                await self.session.refresh(item)
            return user_checklist_items

    async def get_by_user_id(self, user_id: int, completed: bool = None) -> List[UserChecklistItem]:
        stmt = select(UserChecklistItem).where(UserChecklistItem.user_id == user_id)
        if completed is not None:
            stmt = stmt.where(UserChecklistItem.is_completed == completed)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id_and_item_id(self, user_id: int, item_id: int) -> Union[UserChecklistItem, None]:
        stmt = select(UserChecklistItem).where(
            UserChecklistItem.user_id == user_id,
            UserChecklistItem.item_id == item_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_items_with_content_by_checklist_id(self, user_id: int, checklist_id: int) -> List[UserChecklistItem]:
        stmt = (
            select(UserChecklistItem)
            .join(ChecklistItem, UserChecklistItem.item_id == ChecklistItem.id)
            .where(
                UserChecklistItem.user_id == user_id,
                ChecklistItem.checklist_id == checklist_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_completed_by_user_id_and_checklist_id(self, user_id: int, checklist_id: int) -> int:
        stmt = (
            delete(UserChecklistItem)
            .where(UserChecklistItem.user_id == user_id)
            .where(UserChecklistItem.is_completed)
            .where(UserChecklistItem.item_id.in_(
                select(ChecklistItem.id).where(ChecklistItem.checklist_id == checklist_id)
            ))
        )
        result = await self.session.execute(stmt)
        return result.rowcount
