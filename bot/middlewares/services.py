from typing import Callable, Dict, Any
from aiogram import BaseMiddleware

class ServiceMiddleware(BaseMiddleware):
    def __init__(self, dispatcher_kwargs: Dict[str, Any]):
        super().__init__()
        self.dispatcher_kwargs = dispatcher_kwargs

    async def __call__(
        self,
        handler: Callable,
        event: object,
        data: Dict[str, Any]
    ) -> Any:
        session = data.get("session")
        if session is None:
            raise RuntimeError("Session not found in data. DatabaseSessionMiddleware required.")

        # Переделать механизм регистрации репо и сервисов - потом

        user_repo = self.dispatcher_kwargs.get("user_repo")(session)
        campaign_repo = self.dispatcher_kwargs.get("campaign_repo")(session)
        checklist_item_repo = self.dispatcher_kwargs.get("checklist_item_repo")(session)
        checklist_repo = self.dispatcher_kwargs.get("checklist_repo")(session)
        invoice_repo = self.dispatcher_kwargs.get("invoice_repo")(session)
        notification_type_repo = self.dispatcher_kwargs.get("notification_type_repo")(session)
        role_repo = self.dispatcher_kwargs.get("role_repo")(session)
        tariff_repo = self.dispatcher_kwargs.get("tariff_repo")(session)
        user_checklist_item_repo = self.dispatcher_kwargs.get("user_checklist_item_repo")(session)
        user_notification_repo = self.dispatcher_kwargs.get("user_notification_repo")(session)
        user_promocode_repo = self.dispatcher_kwargs.get("user_promocode_repo")(session)
        user_referral_repo = self.dispatcher_kwargs.get("user_referral_repo")(session)
        user_role_repo = self.dispatcher_kwargs.get("user_role_repo")(session)
        user_subscription_repo = self.dispatcher_kwargs.get("user_subscription_repo")(session)
        

        user_service = self.dispatcher_kwargs.get("user_service")(user_repo)
        campaign_service = self.dispatcher_kwargs.get("campaign_service")(campaign_repo)
        checklist_item_service = self.dispatcher_kwargs.get("checklist_item_service")(checklist_item_repo, checklist_repo)
        user_checklist_item_service = self.dispatcher_kwargs.get("user_checklist_item_service")(user_checklist_item_repo, user_repo, checklist_item_repo)
        checklist_service = self.dispatcher_kwargs.get("checklist_service")(checklist_repo)
        invoice_service = self.dispatcher_kwargs.get("invoice_service")(invoice_repo)
        notification_type_service = self.dispatcher_kwargs.get("notification_type_service")(notification_type_repo)
        role_service = self.dispatcher_kwargs.get("role_service")(role_repo)
        tariff_service = self.dispatcher_kwargs.get("tariff_service")(tariff_repo)
        user_notification_service = self.dispatcher_kwargs.get("user_notification_service")(user_notification_repo, notification_type_repo)
        user_promocode_service = self.dispatcher_kwargs.get("user_promocode_service")(user_promocode_repo, campaign_repo, user_repo)
        user_referral_service = self.dispatcher_kwargs.get("user_referral_service")(user_referral_repo, user_repo)
        user_role_service = self.dispatcher_kwargs.get("user_role_service")(user_role_repo, role_repo)
        user_subscription_service = self.dispatcher_kwargs.get("user_subscription_service")(user_subscription_repo, tariff_repo)

        data["user_service"] = user_service
        data["campaign_service"] = campaign_service
        data["checklist_item_service"] = checklist_item_service
        data["user_checklist_item_service"] = user_checklist_item_service
        data["checklist_service"] = checklist_service
        data["invoice_service"] = invoice_service
        data["notification_type_service"] = notification_type_service
        data["role_service"] = role_service
        data["tariff_service"] = tariff_service
        data["user_notification_service"] = user_notification_service
        data["user_promocode_service"] = user_promocode_service
        data["user_referral_service"] = user_referral_service
        data["user_role_service"] = user_role_service
        data["user_subscription_service"] = user_subscription_service

        result = await handler(event, data)
        return result