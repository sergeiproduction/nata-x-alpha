from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from database.repositories.sqlalchemy_repo import AsyncSQLAlchemyRepository
from database.models.user_subscription import UserSubscription
from database.models.tariff import Tariff

class UserSubscriptionRepository(AsyncSQLAlchemyRepository[UserSubscription]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserSubscription)

    async def get_active_subscription(self, user_id: int) -> Optional[UserSubscription]:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.status == "active",
                self.model.expires_at > datetime.now(timezone.utc)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_subscriptions(self, user_id: int) -> List[UserSubscription]:
        stmt = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_expired_subscriptions(self) -> List[UserSubscription]:
        stmt = select(self.model).where(
            and_(
                self.model.status == "active",
                self.model.expires_at <= datetime.now(timezone.utc)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_subscriptions_expiring_soon(self, days: int = 3) -> List[UserSubscription]:
        target_date = datetime.now(timezone.utc) + timedelta(days=days)
        stmt = select(self.model).where(
            and_(
                self.model.status == "active",
                self.model.expires_at > datetime.now(timezone.utc),
                self.model.expires_at <= target_date
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_subscription(
        self,
        user_id: int,
        tariff_id: int,
        starts_at: datetime = None,
        duration_days: int = None
    ) -> UserSubscription:
        from database.models.tariff import Tariff
        
        # Получаем тариф для определения длительности
        tariff_stmt = select(Tariff).where(Tariff.id == tariff_id)
        tariff_result = await self.session.execute(tariff_stmt)
        tariff = tariff_result.scalar_one_or_none()
        
        if not tariff:
            raise ValueError(f"Tariff with id {tariff_id} not found")
        
        # Определяем даты начала и окончания - ВСЕГДА используем aware datetime
        if starts_at is None:
            starts_at = datetime.now(timezone.utc)
        elif starts_at.tzinfo is None:
            # Если передан naive datetime, делаем его aware
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        
        if duration_days is None:
            duration_days = tariff.duration_days
        
        expires_at = starts_at + timedelta(days=duration_days)
        
        # Убедимся, что expires_at тоже aware
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        # Деактивируем старые активные подписки пользователя
        await self.deactivate_user_subscriptions(user_id)
        
        # Создаем новую подписку
        subscription = UserSubscription(
            user_id=user_id,
            tariff_id=tariff_id,
            starts_at=starts_at,
            expires_at=expires_at,
            status="active"
        )
        
        return await self.add(subscription)

    async def deactivate_user_subscriptions(self, user_id: int) -> None:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.status == "active"
            )
        )
        result = await self.session.execute(stmt)
        active_subscriptions = result.scalars().all()
        
        for subscription in active_subscriptions:
            subscription.status = "expired"
            subscription.updated_at = datetime.now(timezone.utc)
            await self.update(subscription)

    async def renew_subscription(
        self,
        user_id: int,
        tariff_id: int,
        additional_days: int = None
    ) -> Optional[UserSubscription]:
        current_subscription = await self.get_active_subscription(user_id)
        
        if current_subscription:
            # Продлеваем существующую подписку
            if additional_days is None:
                tariff_stmt = select(Tariff).where(Tariff.id == tariff_id)
                tariff_result = await self.session.execute(tariff_stmt)
                tariff = tariff_result.scalar_one_or_none()
                additional_days = tariff.duration_days if tariff else 30
            

            # Убедимся, что expires_at — aware datetime
            if current_subscription.expires_at.tzinfo is None:
                current_subscription.expires_at = current_subscription.expires_at.replace(tzinfo=timezone.utc)

            # Продлеваем от текущей даты окончания или от now(), если уже истекла
            extend_from = max(
                current_subscription.expires_at,
                datetime.now(timezone.utc)
            )
            current_subscription.expires_at = extend_from + timedelta(days=additional_days)
            current_subscription.updated_at = datetime.now(timezone.utc)
            
            return await self.update(current_subscription)
        else:
            # Создаем новую подписку
            return await self.create_subscription(user_id, tariff_id)

    async def cancel_subscription(self, user_id: int) -> Optional[UserSubscription]:
        subscription = await self.get_active_subscription(user_id)
        if subscription:
            subscription.status = "canceled"
            subscription.updated_at = datetime.now(timezone.utc)
            return await self.update(subscription)
        return None

    async def is_user_subscription_active(self, user_id: int) -> bool:
        subscription = await self.get_active_subscription(user_id)
        return subscription is not None

    async def get_subscription_with_tariff(self, subscription_id: int) -> Optional[UserSubscription]:
        stmt = select(self.model).where(self.model.id == subscription_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()