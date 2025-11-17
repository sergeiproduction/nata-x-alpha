from typing import List, Union
from schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from database.repositories.campaign_repo import CampaignRepository
from database.models.campaign import Campaign

class CampaignService:
    def __init__(self, campaign_repo: CampaignRepository):
        self.campaign_repo = campaign_repo

    async def create_campaign(self, campaign_data: CampaignCreate) -> CampaignResponse:
        existing = await self.campaign_repo.get_by_name(campaign_data.name)
        if existing:
            return CampaignResponse.model_validate(existing)

        # Проверим логику дат
        if campaign_data.start_date >= campaign_data.end_date:
            raise ValueError("Start date must be before end date.")

        campaign = Campaign(
            name=campaign_data.name,
            description=campaign_data.description,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date
        )
        created = await self.campaign_repo.add(campaign)
        return CampaignResponse.model_validate(created)

    async def get_campaign(self, id: int) -> Union[CampaignResponse, None]:
        campaign = await self.campaign_repo.get(id)
        if campaign:
            return CampaignResponse.model_validate(campaign)
        return None

    async def get_campaign_by_name(self, name: str) -> Union[CampaignResponse, None]:
        campaign = await self.campaign_repo.get_by_name(name)
        if campaign:
            return CampaignResponse.model_validate(campaign)
        return None

    async def list_campaigns(self) -> List[CampaignResponse]:
        campaigns = await self.campaign_repo.list()
        return [CampaignResponse.model_validate(c) for c in campaigns]

    async def get_active_campaigns(self) -> List[CampaignResponse]:
        campaigns = await self.campaign_repo.get_active_campaigns()
        return [CampaignResponse.model_validate(c) for c in campaigns]

    async def get_expired_campaigns(self) -> List[CampaignResponse]:
        campaigns = await self.campaign_repo.get_expired_campaigns()
        return [CampaignResponse.model_validate(c) for c in campaigns]

    async def get_upcoming_campaigns(self, days_ahead: int = 7) -> List[CampaignResponse]:
        campaigns = await self.campaign_repo.get_upcoming_campaigns(days_ahead)
        return [CampaignResponse.model_validate(c) for c in campaigns]

    async def update_campaign(self, id: int, campaign_data: CampaignUpdate) -> Union[CampaignResponse, None]:
        campaign = await self.campaign_repo.get(id)
        if campaign:
            for field, value in campaign_data.model_dump(exclude_unset=True).items():
                setattr(campaign, field, value)
            if campaign.start_date >= campaign.end_date:
                raise ValueError("Start date must be before end date.")
            updated = await self.campaign_repo.update(campaign)
            return CampaignResponse.model_validate(updated)
        return None

    async def delete_campaign(self, id: int) -> bool:
        return await self.campaign_repo.delete(id)
