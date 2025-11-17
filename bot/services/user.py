from typing import List, Union
from schemas.user import UserCreate, UserResponse, UserUpdate
from database.repositories.user_repo import UserRepository
from database.models.user import User

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        existing_user = await self.user_repo.get_by_telegram_id(user_data.telegram_id)
        if existing_user:
            return UserResponse.model_validate(existing_user)

        user = User(name=user_data.name, telegram_id=user_data.telegram_id)
        created_user = await self.user_repo.add(user)
        return UserResponse.model_validate(created_user)

    async def get_user(self, id: int) -> Union[UserResponse, None]:
        user = await self.user_repo.get(id)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def get_user_by_telegram_id(self, telegram_id: int) -> Union[UserResponse, None]:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def list_users(self) -> List[UserResponse]:
        users = await self.user_repo.list()
        return [UserResponse.model_validate(u) for u in users]

    async def update_user(self, id: int, user_data: UserUpdate) -> Union[UserResponse, None]:
        user = await self.user_repo.get(id)
        if user:
            for field, value in user_data.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            updated_user = await self.user_repo.update(user)
            return UserResponse.model_validate(updated_user)
        return None

    async def delete_user(self, id: int) -> bool:
        return await self.user_repo.delete(id)