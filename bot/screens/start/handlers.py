from aiogram import Router, F, flags
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.screens.checklists.user_cases import assign_checklist_to_user
from bot.screens.profile.keyboards import profile_keyboard
from bot.services.campaign import CampaignService
from bot.services.checklist import ChecklistService
from bot.services.checklist_user_item import UserChecklistItemService
from bot.services.image import ImageService
from bot.services.notification_type import NotificationTypeService
from bot.services.tariff import TariffService
from bot.services.user_notification import UserNotificationService
from bot.services.user_promocode import UserPromocodeService
from bot.services.user_subscription import UserSubscriptionService

from schemas.tariff import TariffCreate
from schemas.user import UserCreate, UserResponse

from neural import processor
from schemas.user_subscription import UserSubscriptionCreate
from .states import StartScreen
from .keyboards import start_screen

from bot.screens.startup.keyboards import startup_keyboard

from bot.screens.calendar.keyboards import calendar_keyboard
from bot.screens.calendar.states import CalendarScreen

from bot.screens.accounting.keyboards import accounting_keyboard

from bot.services.user import UserService

from .use_cases import create_promocode, create_user_notification_settings
from utils.templates import load_template_text
from bot.middlewares.user_init import UserInitializationMiddleware

start_router = Router()

start_router.callback_query.middleware(UserInitializationMiddleware())
start_router.message.middleware(UserInitializationMiddleware())


@start_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, 
                    user_service: UserService,
                    user_promocode_service: UserPromocodeService,
                    campaign_service: CampaignService,
                    notification_type_service: NotificationTypeService,
                    user_notification_service: UserNotificationService,
                    checklist_service: ChecklistService,
                    user_checklist_item_service: UserChecklistItemService,
                    tariff_service: TariffService,
                    user_subscription_service: UserSubscriptionService):
    
    user_response = UserCreate(
        name=message.from_user.username,
        telegram_id=message.from_user.id
    )

    # Создаем пользователя (если он новый)
    user = await user_service.create_user(user_response)

    # Получаем или создаем бесплатный тариф
    free_tariff = await tariff_service.get_tariff_by_name("free")
    if not free_tariff:
        # Создаем бесплатный тариф, если его нет
        free_tariff_data = TariffCreate(
            name="free",
            price=0.00,
            duration_days=1000,
            description="Бесплатный тариф",
            features="Базовый функционал"
        )
        free_tariff = await tariff_service.create_tariff(free_tariff_data)

    # Проверяем, есть ли у пользователя активная подписка
    active_subscription = await user_subscription_service.get_active_subscription(user.id)
    
    if not active_subscription:
        # Создаем бесплатную подписку для пользователя, если нет активной
        subscription_data = UserSubscriptionCreate(
            user_id=user.id,
            tariff_id=free_tariff.id
        )
        await user_subscription_service.create_subscription(subscription_data)



    await create_promocode("Бухгалтерия", user.id, user_promocode_service, campaign_service)
    await create_promocode("Приведи друга", user.id, user_promocode_service, campaign_service)


    await create_user_notification_settings(
        user.id,
        notification_type_service,
        user_notification_service,
        ["уведомления", "ФНС", "СФР", "Военкомат", "за 3 дня"]
    )

    await assign_checklist_to_user(user.id, checklist_service, user_checklist_item_service)

    # Получаем все активные чек-листы
    active_checklists = await checklist_service.get_active_checklists()
    
    for checklist in active_checklists:
        await user_checklist_item_service.create_user_checklist_with_items(
            user_id=user.id,
            checklist_id=checklist.id,
            is_completed=False
        )

    text = await load_template_text("start_text")

    await message.answer(text, reply_markup=start_screen())
    await state.set_state(StartScreen.start)


@start_router.message(F.text.casefold().endswith("студенческий стартап"))
async def open_startup(message: Message, state: FSMContext):
    text = await load_template_text("startup_menu")
    await message.answer(text, reply_markup=startup_keyboard())
    await state.clear()


@start_router.message(F.text.casefold().endswith("календарь отчетности"))
async def open_calendar(message: Message, state: FSMContext, 
                        user_repo, user_service: UserService, user_notification_service: UserNotificationService,
                        user_notification_repo, notification_type_repo, 
                        notification_type_service: NotificationTypeService,
                        session):   

    user_repo = user_repo(session)
    user_service = user_service(user_repo)

    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    user_notification_repo = user_notification_repo(session)
    notification_type_repo = notification_type_repo(session)

    await message.answer("Календарь открыт.", reply_markup=await calendar_keyboard(user.id,
        ["уведомления", "ФНС", "СФР", "Военкомат", "за 3 дня"],
        user_notification_service(user_notification_repo, notification_type_repo),
        notification_type_service(notification_type_repo)
    ))

    await state.set_state(CalendarScreen.calendar)


@start_router.message(F.text.casefold().endswith('наши услуги'))
async def open_services(message: Message, state: FSMContext):
    await message.answer("Услуги открыты.")
    await state.clear()


@start_router.message(F.text.casefold().endswith('бухгалтерия'))
async def open_accounting(message: Message, state: FSMContext, user_repo,  user_service: UserService,
                          user_promocode_service: UserPromocodeService, user_promocode_repo,
                          campaign_repo,  session):
    
    info_text = await load_template_text('accounting_info', extended=False)

    user_promocode_service = user_promocode_service(user_promocode_repo(session), campaign_repo(session), user_repo(session))
    user_service = user_service(user_repo(session))

    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    accounting_promocode = await user_promocode_service.get_user_promocode_by_campaign_name(user.id, "Бухгалтерия")
    
    picture = await ImageService.generate_offer(accounting_promocode.name, "./files/accounting.jpg")

    await message.answer_photo(picture, caption=info_text, reply_markup=accounting_keyboard())
    await state.clear()


@start_router.message(F.text.casefold().endswith('профиль'))
async def open_profile(message: Message, user: UserResponse,
                        tariff_service: TariffService,
                        user_subscription_service: UserSubscriptionService,
                        user_promocode_service: UserPromocodeService,):

    
    user_tariff = await user_subscription_service.get_active_subscription(user_id=user.id)
    
    if user_tariff is None:

        free_tariff = await tariff_service.get_tariff_by_name("free")

        subscription_data = UserSubscriptionCreate(
            user_id=user.id,
            tariff_id=free_tariff.id,
            duration_days=1000
        )

        user_tariff = await user_subscription_service.create_subscription(subscription_data)

    expire_date = await user_subscription_service.get_subscription_expiry_date(user.id)

    is_premium = True if user_tariff.tariff_name == "premium" else False

    text = await load_template_text("subscription_info", templates_dir="./templates/profile/",
                                    is_premium = is_premium,
                                    subscription_end_date=expire_date.strftime("%d.%m.%Y"))

    
    referral_promocode = await user_promocode_service.get_user_promocode_by_campaign_name(user.id, "Приведи друга")

    picture = await ImageService.generate_offer(referral_promocode.name, "./files/referal.jpg")

    await message.answer_photo(picture, caption=text, reply_markup=profile_keyboard(is_premium))

