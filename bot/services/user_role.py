from typing import Union, List
from schemas.user_role import UserRoleCreate, UserRoleResponse
from database.repositories.user_role_repo import UserRoleRepository
from database.repositories.role_repo import RoleRepository
from database.models.user_role import UserRole

class UserRoleService:
    def __init__(self, user_role_repo: UserRoleRepository, role_repo: RoleRepository):
        self.user_role_repo = user_role_repo
        self.role_repo = role_repo

    async def assign_role_to_user(self, user_role_data: UserRoleCreate) -> Union[UserRoleResponse, None]:
        role = await self.role_repo.get(user_role_data.role_id)
        if not role:
            return None

        existing = await self.user_role_repo.get_by_user_id_and_role_id(user_role_data.user_id, user_role_data.role_id)
        if existing:
            return UserRoleResponse.model_validate(existing)

        user_role = UserRole(
            user_id=user_role_data.user_id,
            role_id=user_role_data.role_id
        )
        created_user_role = await self.user_role_repo.add(user_role)
        return UserRoleResponse.model_validate(created_user_role)

    async def get_user_roles(self, user_id: int) -> List[str]:
        return await self.user_role_repo.get_roles_by_user_id(user_id)

    async def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        return await self.user_role_repo.delete_by_user_id_and_role_id(user_id, role_id)

    async def remove_role_from_user_by_name(self, user_id: int, role_name: str) -> bool:
        return await self.user_role_repo.delete_by_user_id_and_role_name(user_id, role_name)

    async def remove_all_roles_from_user(self, user_id: int) -> int:
        return await self.user_role_repo.delete_by_user_id(user_id)

    async def get_user_role_links(self, user_id: int) -> List[UserRoleResponse]:
        user_roles = await self.user_role_repo.get_by_user_id(user_id)
        return [UserRoleResponse.model_validate(ur) for ur in user_roles]