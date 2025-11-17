from aiogram import Bot, Dispatcher, Router
import asyncio
from bot.middlewares.database import DatabaseSessionMiddleware
from bot.middlewares.services import ServiceMiddleware
from bot.tasks.report_notification import start_daily_notification_task
from config import BOT_TOKEN
from neural_config import processor
from bot.screens import (
    start_router, startup_router, calendar_router,
    account_router, profile_router, privacy_router,
    services_router, support_router, 
    checklist_router, faq_router, survey_router,
    passport_router, all_router
)
from bot.screens.survey.middlewares import SubscriptionCheckMiddleware


from database.session import with_db_session
from setup import create_base_campaign, create_notification_type, create_roles, dispatcher_kwargs


bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(**dispatcher_kwargs)



subscription_midlleware = SubscriptionCheckMiddleware(
        tariff_service=dispatcher_kwargs.get("tariff_service"),
        user_subscription_service=dispatcher_kwargs.get("user_subscription_service"),
        user_service=dispatcher_kwargs.get("user_service"),
        user_repo=dispatcher_kwargs.get("user_repo"),
        user_subscription_repo=dispatcher_kwargs.get("user_subscription_repo"),
        tariff_repo=dispatcher_kwargs.get("tariff_repo")
    )


dp.message.outer_middleware(DatabaseSessionMiddleware())
dp.callback_query.outer_middleware(DatabaseSessionMiddleware())

dp.message.outer_middleware(ServiceMiddleware(dispatcher_kwargs))
dp.callback_query.outer_middleware(ServiceMiddleware(dispatcher_kwargs))

routers = [
    start_router,
    startup_router,
    calendar_router,
    services_router,
    account_router,
    profile_router,
    support_router,
    privacy_router,
    checklist_router,
    faq_router,
    survey_router,
    passport_router,
    all_router  
]

dp.include_routers(*routers)


async def setup_routers(*routers: Router, middleware):
    for router in routers:
        router.callback_query.middleware(middleware)
        router.message.middleware(middleware)
    

@with_db_session
async def on_startup(session):
    await create_base_campaign(session, "Бухгалтерия", "Партнерская программа по бухгалтерии")
    await create_base_campaign(session, "Приведи друга", "Рекомендация друзьям")
    await create_roles(session, ["admin", "user", "partner"])

    await create_notification_type(session, "уведомления")
    await create_notification_type(session, "ФНС")
    await create_notification_type(session, "СФР")
    await create_notification_type(session, "Военкомат")
    await create_notification_type(session, "за 3 дня", advance_days=3)

    await setup_routers(*routers, middleware=subscription_midlleware)


@with_db_session
async def start_tasks(**kwargs):
    session = kwargs["session"]
    await start_daily_notification_task(
        notification_type_service=dispatcher_kwargs.get("notification_type_service")(
            dispatcher_kwargs.get("notification_type_repo")(session)
        ),
        user_notification_service=dispatcher_kwargs.get("user_notification_service")(
            dispatcher_kwargs.get("user_notification_repo")(session),
            dispatcher_kwargs.get("notification_type_repo")(session)
        ),
        user_service=dispatcher_kwargs.get("user_service")(
            dispatcher_kwargs.get("user_repo")(session)
        ),
        bot=bot
    )



async def main():

    await on_startup()
    
    asyncio.create_task(
        start_tasks()
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())