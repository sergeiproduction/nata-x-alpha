from typing import List
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

from bot.services.notification_type import NotificationTypeService
from bot.services.user_notification import UserNotificationService

async def calendar_keyboard(user_id: int, notification_names: List[str],
                             user_notification_service: UserNotificationService, 
                             notification_type_service: NotificationTypeService):
    notification_status = {}
    
    user_notifications = await user_notification_service.get_user_notifications(user_id)

    for notification in user_notifications:
        notification_type = await notification_type_service.get_notification_type(notification.notification_type_id)

        if notification_type.name in notification_names:
            notification_status[notification_type.name.lower()] = notification.is_active

    enable = "🟢"
    disable = "🔴"

    builder = ReplyKeyboardBuilder()
    
    all_notification = enable if notification_status.get("уведомления") else disable 

    builder.add(KeyboardButton(text=f"Уведомления {all_notification}"))

    fns_status = enable if notification_status.get("фнс") else disable
    sfr_status = enable if notification_status.get("сфр") else disable  
    voen_status = enable if notification_status.get("военкомат") else disable
   
    builder.row(
        KeyboardButton(text=f"ФНС {fns_status}"),
        KeyboardButton(text=f"СФР {sfr_status}"),
        KeyboardButton(text=f"Военкомат {voen_status}")
    )
    
    three_days_status = enable if notification_status.get("за 3 дня", False) else disable
    
    builder.row(
        KeyboardButton(text=f"За 3 дня {three_days_status}"),
        KeyboardButton(text="На неделю")
    )

    builder.row(
        KeyboardButton(text="Календарь на месяц"),
        KeyboardButton(text="Назад")
    )
    
    return builder.as_markup(resize_keyboard=True)