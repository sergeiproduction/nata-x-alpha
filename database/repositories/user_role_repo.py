from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.models.role import Role
from database.models.user_role import UserRole
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository


class UserRoleRepository(AsyncSQLAlchemyRepository[UserRole]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserRole)

    # Пример специфичного метода
    async def get_by_user_id(self, user_id: int) -> List[UserRole]:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # Пример метода: удалить все роли у пользователя
    async def delete_by_user_id(self, user_id: int) -> int:
        """
        Удаляет все записи UserRole для конкретного пользователя.
        Возвращает количество удалённых записей.
        """
        stmt = delete(UserRole).where(UserRole.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    # Пример метода: получить все роли пользователя (через JOIN)
    async def get_roles_by_user_id(self, user_id: int) -> List[str]:
        """
        Возвращает список названий ролей для пользователя.
        """
        stmt = (
            select(Role.name)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all() # Возвращает список строк (имён ролей)

    # Новый метод: удалить конкретную роль у пользователя по наименованию (уже был)
    async def delete_by_user_id_and_role_name(self, user_id: int, role_name: str) -> bool:
        """
        Удаляет конкретную роль у пользователя по наименованию роли.
        Возвращает True, если роль была найдена и удалена, иначе False.
        """
        stmt = (
            delete(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == select(Role.id).where(Role.name == role_name).scalar_subquery())
        )
        result = await self.session.execute(stmt)
        deleted_count = result.rowcount
        return deleted_count > 0

    # Новый метод: получить связь по user_id и role_id
    async def get_by_user_id_and_role_id(self, user_id: int, role_id: int) -> Union[UserRole, None]:
        """
        Получает запись UserRole по user_id и role_id.
        """
        stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # Новый метод: удалить связь по user_id и role_id
    async def delete_by_user_id_and_role_id(self, user_id: int, role_id: int) -> bool:
        """
        Удаляет конкретную роль у пользователя по role_id.
        Возвращает True, если роль была найдена и удалена, иначе False.
        """
        stmt = delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        result = await self.session.execute(stmt)
        deleted_count = result.rowcount
        return deleted_count > 0