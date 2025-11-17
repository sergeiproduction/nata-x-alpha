from typing import Union, List
from database.repositories.user_repo import UserRepository
from schemas.user_referral import UserReferralCreate, UserReferralResponse
from database.repositories.user_referral_repo import UserReferralRepository
from database.models.user_referral import UserReferral

class UserReferralService:
    def __init__(self, user_referral_repo: UserReferralRepository, user_repo: UserRepository): # <-- Добавляем user_repo
        self.user_referral_repo = user_referral_repo
        self.user_repo = user_repo

    async def create_referral(self, referral_data: UserReferralCreate) -> Union[UserReferralResponse, None]:

        if referral_data.user_id == referral_data.referrer_id:
            return None

        user_exists = await self.user_repo.get(referral_data.user_id) is not None
        if not user_exists:
            raise ValueError(f"User with id {referral_data.user_id} does not exist.")

        referrer_exists = await self.user_repo.get(referral_data.referrer_id) is not None
        if not referrer_exists:
            raise ValueError(f"Referrer with id {referral_data.referrer_id} does not exist.")

        existing = await self.user_referral_repo.get_by_user_id_and_referrer_id(
            referral_data.user_id, referral_data.referrer_id
        )
        if existing:
            return UserReferralResponse.model_validate(existing)

        referral = UserReferral(
            user_id=referral_data.user_id,
            referrer_id=referral_data.referrer_id
        )
        created_referral = await self.user_referral_repo.add(referral)
        return UserReferralResponse.model_validate(created_referral)

    async def get_referrals_by_user_id(self, user_id: int) -> List[UserReferralResponse]:
        referrals = await self.user_referral_repo.get_referrals_by_user_id(user_id)
        return [UserReferralResponse.model_validate(r) for r in referrals]

    async def get_referrer_by_referee_id(self, referrer_id: int) -> Union[UserReferralResponse, None]:
        referral = await self.user_referral_repo.get_referrer_by_referee_id(referrer_id)
        if referral:
            return UserReferralResponse.model_validate(referral)
        return None

    async def remove_referral(self, user_id: int, referrer_id: int) -> bool:
        return await self.user_referral_repo.delete_referral(user_id, referrer_id)

    async def get_referral_by_user_and_referrer(self, user_id: int, referrer_id: int) -> Union[UserReferral, None]:
        return await self.user_referral_repo.get_by_user_id_and_referrer_id(user_id, referrer_id)