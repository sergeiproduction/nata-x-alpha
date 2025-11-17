import string
from typing import List

from bot.services.campaign import CampaignService
from bot.services.notification_type import NotificationTypeService
from bot.services.user_notification import UserNotificationService
from bot.services.user_promocode import UserPromocodeService
from schemas.user_notification import UserNotificationCreate
from schemas.user_promocode import UserPromocodeCreate
from utils.generator import CodeGenerator


async def create_promocode(campaign_name: str, user_id: int, promocode_serivce: UserPromocodeService, campaign_service: CampaignService):

    generator = CodeGenerator(string.ascii_uppercase)

    promocode = generator.generate_code()
    while await promocode_serivce.promocode_exist(promocode):
        promocode = generator.generate_code()

    campaign = await campaign_service.get_campaign_by_name(campaign_name)

    await promocode_serivce.create_user_promocode(
        UserPromocodeCreate(
            campaign_id=campaign.id,
            user_id=user_id,
            name=promocode
        )
    )



async def create_user_notification_settings(user_id: int, notification_type_service: NotificationTypeService, user_notification_service: UserNotificationService, notification_names: List[str] = None):
    """Creates default notification settings for a new user"""
    if notification_names is None:
        # Если список не указан, используем все существующие типы
        all_notification_types = await notification_type_service.list_notification_types()
    else:
        # Получаем все типы и фильтруем по указанным именам
        all_notification_types = await notification_type_service.list_notification_types()
        all_notification_types = [nt for nt in all_notification_types if nt.name in notification_names]

    # Создаем пользовательские настройки для найденных типов
    for notification_type in all_notification_types:
        user_notification_data = UserNotificationCreate(
            user_id=user_id,
            notification_type_id=notification_type.id,
            is_active=notification_type.default_enabled
        )
        await user_notification_service.create_user_notification(user_notification_data)