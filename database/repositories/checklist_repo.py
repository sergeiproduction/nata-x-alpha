from typing import Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.checklist import Checklist
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class ChecklistRepository(AsyncSQLAlchemyRepository[Checklist]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Checklist)

    async def get_by_name(self, name: str) -> Union[Checklist, None]:
        stmt = select(Checklist).where(Checklist.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_checklists(self) -> List[Checklist]:
        stmt = select(Checklist).where(Checklist.is_active)
        result = await self.session.execute(stmt)
        return result.scalars().all()