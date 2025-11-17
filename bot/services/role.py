from typing import List, Union
from schemas.role import RoleCreate, RoleResponse, RoleUpdate
from database.repositories.role_repo import RoleRepository
from database.models.role import Role

class RoleService:
    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        existing_role = await self.role_repo.get_by_name(role_data.name)
        if existing_role:
            return RoleResponse.model_validate(existing_role)

        role = Role(name=role_data.name)
        created_role = await self.role_repo.add(role)
        return RoleResponse.model_validate(created_role)

    async def get_role(self, id: int) -> Union[RoleResponse, None]:
        role = await self.role_repo.get(id)
        if role:
            return RoleResponse.model_validate(role)
        return None

    async def get_role_by_name(self, name: str) -> Union[RoleResponse, None]:
        role = await self.role_repo.get_by_name(name)
        if role:
            return RoleResponse.model_validate(role)
        return None

    async def list_roles(self) -> List[RoleResponse]:
        roles = await self.role_repo.list()
        return [RoleResponse.model_validate(r) for r in roles]

    async def update_role(self, id: int, role_data: RoleUpdate) -> Union[RoleResponse, None]:
        role = await self.role_repo.get(id)
        if role:
            for field, value in role_data.model_dump(exclude_unset=True).items():
                setattr(role, field, value)
            updated_role = await self.role_repo.update(role)
            return RoleResponse.model_validate(updated_role)
        return None

    async def delete_role(self, id: int) -> bool:
        return await self.role_repo.delete(id)