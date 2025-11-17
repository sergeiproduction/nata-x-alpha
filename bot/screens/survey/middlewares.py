from datetime import datetime, timezone
from typing import Callable, Dict, Any, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from database.session import with_db_session
from bot.services.tariff import TariffService
from bot.services.user_subscription import UserSubscriptionService
from bot.services.user import UserService
from schemas.user_subscription import UserSubscriptionCreate

class SubscriptionCheckMiddleware(BaseMiddleware):
    def __init__(
        self,
        tariff_service: TariffService,
        user_subscription_service: UserSubscriptionService,
        user_service: UserService,
        user_repo,
        user_subscription_repo,
        tariff_repo,
    ):
        super().__init__()
        self.tariff_service = tariff_service
        self.user_subscription_service = user_subscription_service
        self.user_service = user_service
        self.user_repo = user_repo
        self.user_subscription_repo = user_subscription_repo
        self.tariff_repo = tariff_repo

    @with_db_session
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
        session) -> Any:

        # Получаем пользователя из контекста
        user: Optional[User] = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        # Создаём экземпляры сервисов с сессией
        user_service_instance: UserService = self.user_service(self.user_repo(session))
        user_subscription_service: UserSubscriptionService = self.user_subscription_service(
            self.user_subscription_repo(session), self.tariff_repo(session)
        )
        tariff_service_instance: TariffService = self.tariff_service(self.tariff_repo(session))

        # Получаем пользователя из БД по telegram_id
        db_user = await user_service_instance.get_user_by_telegram_id(user.id)
        if not db_user:
            return await handler(event, data)

        # Получаем активную подписку
        subscription = await user_subscription_service.get_active_subscription(db_user.id)

        if subscription:
            # Проверяем, не истекла ли подписка
            now = datetime.now(timezone.utc)
            expires_at = subscription.expires_at

            # Приводим expires_at к aware datetime, если он naive
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at <= now:
                # Подписка истекла - отменяем её
                await user_subscription_service.cancel_subscription(db_user.id)

                # Находим бесплатный тариф (обычно это тариф с именем "free")
                free_tariff = await tariff_service_instance.get_tariff_by_name("free")
                if free_tariff:
                    # Создаём новую подписку с бесплатным тарифом
                    await user_subscription_service.create_subscription(
                        UserSubscriptionCreate(
                            user_id=db_user.id,
                            tariff_id=free_tariff.id,
                            duration_days=free_tariff.duration_days
                        )
                    )

        return await handler(event, data)