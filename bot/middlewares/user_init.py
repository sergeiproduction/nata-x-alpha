from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.services.user import UserService
from bot.services.user_subscription import UserSubscriptionService
from bot.services.tariff import TariffService
from schemas.user import User


class UserInitializationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: object,
        data: Dict[str, Any]
    ) -> Any:
        user_service: UserService = data.get("user_service")
        if user_service is None:
            raise RuntimeError("user_service not found in data. ServiceMiddleware required.")

        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id is None:
            return await handler(event, data)

        user = await user_service.get_user_by_telegram_id(user_id)

        user_subscription_service: UserSubscriptionService = data.get("user_subscription_service")

        subscription = await user_subscription_service.get_active_subscription(user.id)
        
        tariff_service: TariffService = data.get("tariff_service")
        tarrif = await tariff_service.get_tariff(subscription.id)

        is_premium = True if tarrif.name == "premium" else False 

        user_data = User(
            name=user.name,
            id=user.id,
            telegram_id=user.telegram_id,
            inn = user.inn,
            is_premium = is_premium 
        )

        data["user"] = user_data

        result = await handler(event, data)
        return result