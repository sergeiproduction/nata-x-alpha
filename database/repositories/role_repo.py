from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.role import Role
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository

class RoleRepository(AsyncSQLAlchemyRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Role)

    async def get_by_name(self, name: str) -> Union[Role, None]:
        stmt = select(Role).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()