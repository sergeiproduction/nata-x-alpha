from typing import List, Optional
from datetime import datetime, timezone
from schemas.user_subscription import UserSubscriptionCreate, UserSubscriptionResponse, SubscriptionRenew
from database.repositories.user_subscription_repo import UserSubscriptionRepository
from database.repositories.tariff_repo import TariffRepository
from database.models.user_subscription import UserSubscription

class UserSubscriptionService:
    def __init__(self, subscription_repo: UserSubscriptionRepository, tariff_repo: TariffRepository):
        self.subscription_repo = subscription_repo
        self.tariff_repo = tariff_repo

    async def create_subscription(self, subscription_data: UserSubscriptionCreate) -> UserSubscriptionResponse:
        tariff = await self.tariff_repo.get(subscription_data.tariff_id)
        if not tariff:
            raise ValueError(f"Tariff with id {subscription_data.tariff_id} not found")

        active_subscription = await self.subscription_repo.get_active_subscription(subscription_data.user_id)
        if active_subscription:
            raise ValueError("User already has an active subscription")

        # Создаем подписку
        subscription = await self.subscription_repo.create_subscription(
            user_id=subscription_data.user_id,
            tariff_id=subscription_data.tariff_id,
            duration_days=subscription_data.duration_days
        )

        return await self._enrich_subscription_response(subscription)

    async def get_active_subscription(self, user_id: int) -> Optional[UserSubscriptionResponse]:
        subscription = await self.subscription_repo.get_active_subscription(user_id)
        if subscription:
            return await self._enrich_subscription_response(subscription)
        return None

    async def get_user_subscriptions(self, user_id: int) -> List[UserSubscriptionResponse]:
        subscriptions = await self.subscription_repo.get_user_subscriptions(user_id)
        return [await self._enrich_subscription_response(sub) for sub in subscriptions]

    async def renew_subscription(self, user_id: int, renew_data: SubscriptionRenew) -> Optional[UserSubscriptionResponse]:
        tariff = await self.tariff_repo.get(renew_data.tariff_id)
        if not tariff:
            raise ValueError(f"Tariff with id {renew_data.tariff_id} not found")

        subscription = await self.subscription_repo.renew_subscription(
            user_id=user_id,
            tariff_id=renew_data.tariff_id,
            additional_days=renew_data.additional_days
        )

        if subscription:
            return await self._enrich_subscription_response(subscription)
        return None

    async def cancel_subscription(self, user_id: int) -> Optional[UserSubscriptionResponse]:
        subscription = await self.subscription_repo.cancel_subscription(user_id)
        if subscription:
            return await self._enrich_subscription_response(subscription)
        return None

    async def is_subscription_active(self, user_id: int) -> bool:
        return await self.subscription_repo.is_user_subscription_active(user_id)

    async def get_days_remaining(self, user_id: int) -> Optional[int]:
        subscription = await self.subscription_repo.get_active_subscription(user_id)
        if subscription:
            now = datetime.now(timezone.utc)
            if subscription.expires_at > now:
                return (subscription.expires_at - now).days
        return None

    async def get_expiring_subscriptions(self, days: int = 3) -> List[UserSubscriptionResponse]:
        subscriptions = await self.subscription_repo.get_subscriptions_expiring_soon(days)
        return [await self._enrich_subscription_response(sub) for sub in subscriptions]

    async def get_expired_subscriptions(self) -> List[UserSubscriptionResponse]:
        subscriptions = await self.subscription_repo.get_expired_subscriptions()
        return [await self._enrich_subscription_response(sub) for sub in subscriptions]


    async def get_subscription_expiry_date(self, user_id: int) -> Optional[datetime]:
        subscription = await self.subscription_repo.get_active_subscription(user_id)
        if subscription and subscription.status == "active":
            return subscription.expires_at
        return None

    async def _enrich_subscription_response(self, subscription: UserSubscription) -> UserSubscriptionResponse:
        # Получаем информацию о тарифе
        tariff = await self.tariff_repo.get(subscription.tariff_id)
        tariff_name = tariff.name if tariff else "Unknown"

        # Вычисляем оставшиеся дни с правильной обработкой timezone
        now = datetime.now(timezone.utc)
        days_remaining = None
        
        if subscription.status == "active":
            # Приводим expires_at к aware datetime для сравнения
            expires_at = subscription.expires_at
            
            # Если expires_at naive (без timezone), делаем его aware
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            # Теперь оба datetime aware и можно сравнивать
            if expires_at > now:
                days_remaining = (expires_at - now).days

        # Создаем обогащенный ответ
        response_data = {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "tariff_id": subscription.tariff_id,
            "tariff_name": tariff_name,
            "starts_at": subscription.starts_at,
            "expires_at": subscription.expires_at,
            "status": subscription.status,
            "created_at": subscription.created_at,
            "updated_at": subscription.updated_at,
            "days_remaining": days_remaining
        }

        return UserSubscriptionResponse(**response_data)