from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext


from bot.screens import CalendarScreen, StartScreen
from bot.screens import start_screen
from bot.services.notification_type import NotificationTypeService
from bot.services.user import UserService
from bot.services.user_notification import UserNotificationService
from schemas.user_notification import UserNotificationUpdate


from .use_cases import show_report_ahead, update_notification_settings
from .keyboards import calendar_keyboard

from neural import processor

calendar_router = Router()


@calendar_router.message(Command("calendar"))
async def cmd_calendar(message: Message, state: FSMContext, user_service: UserService,
                        user_notification_service: UserNotificationService, notification_type_service: NotificationTypeService):

    user = await user_service.get_user_by_telegram_id(message.from_user.id)
 
    await message.answer("Уведомления переключены.", reply_markup=await calendar_keyboard(user.id,
        ["уведомления", "ФНС", "СФР", "Военкомат", "за 3 дня"],
        user_notification_service,
        notification_type_service
    ))
    await state.set_state(CalendarScreen.calendar)



@calendar_router.message(StateFilter(CalendarScreen.calendar), F.text.casefold().contains("уведомления"))
async def toggle_all_notifications(message: Message, user_service: UserService,
                                user_notification_service: UserNotificationService,
                                notification_type_service: NotificationTypeService):
    
    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    notification_type = await notification_type_service.get_notification_type_by_name("уведомления")
    notification_status = await user_notification_service.get_user_notification(user.id, notification_type.id)

    notifications = ["уведомления", "ФНС", "СФР", "Военкомат", "за 3 дня"]

    for notification in notifications:
        notification_type = await notification_type_service.get_notification_type_by_name(notification)
        await user_notification_service.update_user_notification(
            user.id,
            notification_type.id,
            UserNotificationUpdate(is_active=not notification_status.is_active)
        )

    await message.answer("Уведомления переключены.", reply_markup=await calendar_keyboard(user.id,
        notifications,
        user_notification_service,
        notification_type_service
    ))


@calendar_router.message(F.text.contains("ФНС"), StateFilter(CalendarScreen.calendar))
async def toggle_fns(message: Message, user_service: UserService,
                    user_notification_service: UserNotificationService,
                    notification_type_service: NotificationTypeService):
    
    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    await update_notification_settings(
        user.id, "ФНС",
        user_notification_service,
        notification_type_service,        
    )

    await message.answer("Уведомления переключены.", reply_markup=await calendar_keyboard(user.id,
        ["уведомления", "ФНС", "СФР", "Военкомат", "за 3 дня"],
        user_notification_service,
        notification_type_service
    ))


@calendar_router.message(F.text.contains("СФР"), StateFilter(CalendarScreen.calendar))
async def toggle_sfr(message: Message, user_service: UserService, 
                     user_notification_service: UserNotificationService, notification_type_service: NotificationTypeService):
    
    
    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    await update_notification_settings(
        user.id, "СФР",
        user_notification_service,
        notification_type_service,        
    )
    
    await message.answer("Уведомления переключены.", reply_markup=await calendar_keyboard(user.id,
        ["уведомления", "ФНС", "СФР", "Военкомат", "за 3 дня"],
        user_notification_service,
        notification_type_service
    ))

@calendar_router.message(F.text.contains("Военкомат"), StateFilter(CalendarScreen.calendar))
async def toggle_military(message: Message, user_service: UserService, 
                        user_notification_service: UserNotificationService, notification_type_service: NotificationTypeService):


    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    await update_notification_settings(
        user.id, "Военкомат",
        notification_type_service,
        user_notification_service,        
    )
    
    await message.answer("Уведомления переключены.", reply_markup=await calendar_keyboard(user.id,
        ["уведомления", "ФНС", "СФР", "Военкомат", "за 3 дня"],
        user_notification_service,
        notification_type_service
    ))


@calendar_router.message(F.text.contains("За 3 дня"), StateFilter(CalendarScreen.calendar))
async def toggle_three_days(message: Message, user_service: UserService, 
                            user_notification_service: UserNotificationService, notification_type_service: NotificationTypeService):
    

    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    await update_notification_settings(
        user.id, "за 3 дня",
        notification_type_service,
        user_notification_service,        
    )
    
    await message.answer("Уведомления переключены.", reply_markup=await calendar_keyboard(user.id,
        ["уведомления", "ФНС", "СФР", "Военкомат", "за 3 дня"],
        user_notification_service,
        notification_type_service
    ))


@calendar_router.message(F.text.contains("На неделю"), StateFilter(CalendarScreen.calendar))
async def toggle_week_days(message: Message):
    calendar = await show_report_ahead(days=7)

    await message.answer(calendar)

@calendar_router.message(F.text.contains("Календарь на месяц"), StateFilter(CalendarScreen.calendar))
async def show_month_calendar(message: Message):    
    calendar = await show_report_ahead(days=30)

    await message.answer(calendar)



@calendar_router.message(F.text == "Назад", StateFilter(CalendarScreen.calendar))
async def back_to_main_menu(message: Message, state: FSMContext):
    await message.answer("Возвращаемся в главное меню.", reply_markup=start_screen())
    await state.set_state(StartScreen.start)