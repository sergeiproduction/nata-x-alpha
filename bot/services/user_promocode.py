from typing import Union, List
from schemas.user_promocode import UserPromocodeCreate, UserPromocodeResponse, UserPromocodeUpdate
from database.repositories.user_promocode_repo import UserPromocodeRepository
from database.repositories.campaign_repo import CampaignRepository
from database.repositories.user_repo import UserRepository
from database.models.user_promocode import UserPromocode

class UserPromocodeService:
    def __init__(self, user_promocode_repo: UserPromocodeRepository, campaign_repo: CampaignRepository, user_repo: UserRepository):
        self.user_promocode_repo = user_promocode_repo
        self.campaign_repo = campaign_repo
        self.user_repo = user_repo

    async def create_user_promocode(self, user_promocode_data: UserPromocodeCreate) -> Union[UserPromocodeResponse, None]:
        campaign = await self.campaign_repo.get(user_promocode_data.campaign_id)
        if not campaign:
            return None
        
        user = await self.user_repo.get(user_promocode_data.user_id)
        if not user:
            return None

        existing = await self.user_promocode_repo.get_by_user_id_and_campaign_id(
            user_promocode_data.user_id, user_promocode_data.campaign_id
        )
        if existing:
            return UserPromocodeResponse.model_validate(existing)

        user_promocode = UserPromocode(
            campaign_id=user_promocode_data.campaign_id,
            user_id=user_promocode_data.user_id,
            name=user_promocode_data.name
        )
        created = await self.user_promocode_repo.add(user_promocode)
        return UserPromocodeResponse.model_validate(created)

    async def get_user_promocode(self, id: int) -> Union[UserPromocodeResponse, None]:
        user_promocode = await self.user_promocode_repo.get(id)
        if user_promocode:
            return UserPromocodeResponse.model_validate(user_promocode)
        return None

    async def get_user_promocode_by_campaign_name(self, user_id: int, campaign_name: str) -> Union[UserPromocodeResponse, None]:
        campaign = await self.campaign_repo.get_by_name(campaign_name)

        if not campaign:
            return None

        user_promocode = await self.user_promocode_repo.get_by_user_id_and_campaign_id(user_id, campaign.id)

        if not user_promocode:
            return None        
        
        return UserPromocodeResponse.model_validate(user_promocode)

    async def get_user_promocodes(self, user_id: int) -> List[UserPromocodeResponse]:
        user_promocodes = await self.user_promocode_repo.get_by_user_id(user_id)
        return [UserPromocodeResponse.model_validate(up) for up in user_promocodes]

    async def get_campaign_promocodes(self, campaign_id: int) -> List[UserPromocodeResponse]:
        user_promocodes = await self.user_promocode_repo.get_by_campaign_id(campaign_id)
        return [UserPromocodeResponse.model_validate(up) for up in user_promocodes]

    async def get_active_promocodes_by_user(self, user_id: int) -> List[UserPromocodeResponse]:
        user_promocodes = await self.user_promocode_repo.get_active_promocodes_by_user_id(user_id)
        return [UserPromocodeResponse.model_validate(up) for up in user_promocodes]

    async def get_user_by_promocode(self, promocode: str) -> Union[UserPromocodeResponse, None]:
        user_promocode = await self.user_promocode_repo.get_by_name(promocode)
        return UserPromocodeResponse.model_validate(user_promocode)

    async def promocode_exist(self, promocode: str) -> bool:
        promocode = await self.user_promocode_repo.get_by_name(promocode)

        return True if promocode is not None else False

    async def update_user_promocode(self, id: int, user_promocode_data: UserPromocodeUpdate) -> Union[UserPromocodeResponse, None]:
        user_promocode = await self.user_promocode_repo.get(id)
        if user_promocode:
            for field, value in user_promocode_data.model_dump(exclude_unset=True).items():
                setattr(user_promocode, field, value)
            updated = await self.user_promocode_repo.update(user_promocode)
            return UserPromocodeResponse.model_validate(updated)
        return None

    async def delete_user_promocode(self, id: int) -> bool:
        return await self.user_promocode_repo.delete(id)

    async def delete_user_promocodes_by_user_and_campaign(self, user_id: int, campaign_id: int) -> int:
        return await self.user_promocode_repo.delete_by_user_id_and_campaign_id(user_id, campaign_id)
