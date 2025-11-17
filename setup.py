from datetime import datetime, timedelta, timezone
from typing import List
from bot.services.campaign import CampaignService
from bot.services.notification_type import NotificationTypeService
from bot.services.role import RoleService
from database.repositories.role_repo import RoleRepository
from schemas.campaign import CampaignCreate
from schemas.notification_type import NotificationTypeCreate, NotificationTypeResponse
from schemas.role import RoleCreate
from utils.auto_importer import build_dispatcher_kwargs

dispatcher_kwargs = build_dispatcher_kwargs("./database/repositories", "./bot/services")


async def create_base_campaign(session, campaign_name: str, description: str):
    campaign_repo = dispatcher_kwargs.get("campaign_repo")(session)
    campaign_service: CampaignService = dispatcher_kwargs.get("campaign_service")(campaign_repo)

    if not await campaign_service.get_campaign_by_name(campaign_name):
        campaign_data = CampaignCreate(
            name = campaign_name,
            description=description,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=31*200)
        )
        await campaign_service.create_campaign(campaign_data)


async def create_roles(session, roles: List[str]):
    role_repo: RoleRepository = dispatcher_kwargs.get("role_repo")(session)
    role_service: RoleService = dispatcher_kwargs.get("role_service")(role_repo)

    for role in roles:
        if role not in await role_repo.list():
            await role_service.create_role(RoleCreate(name=role))


async def create_notification_type(session, name: str, advance_days: int = 1) -> NotificationTypeResponse:
    """Creates a notification type with optional advance days setting"""
    
    notification_type_repo = dispatcher_kwargs.get("notification_type_repo")(session)
    notification_type_service: NotificationTypeService = dispatcher_kwargs.get("notification_type_service")(notification_type_repo)

    
    notification_type_data = NotificationTypeCreate(
        name=name,
        description=f"Тип уведомления для {name}",
        default_enabled=True,
        advance_days=advance_days
    )
    return await notification_type_service.create_notification_type(notification_type_data)


