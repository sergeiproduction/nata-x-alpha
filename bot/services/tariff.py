from typing import List, Optional
from schemas.tariff import TariffCreate, TariffResponse, TariffUpdate
from database.repositories.tariff_repo import TariffRepository

class TariffService:
    def __init__(self, tariff_repo: TariffRepository):
        self.tariff_repo = tariff_repo

    async def create_tariff(self, tariff_data: TariffCreate) -> TariffResponse:
        existing_tariff = await self.tariff_repo.get_by_name(tariff_data.name)
        if existing_tariff:
            raise ValueError(f"Tariff with name '{tariff_data.name}' already exists")

        tariff = await self.tariff_repo.create_tariff(
            name=tariff_data.name,
            price=tariff_data.price,
            duration_days=tariff_data.duration_days,
            description=tariff_data.description,
            features=tariff_data.features
        )
        return TariffResponse.model_validate(tariff)

    async def get_tariff(self, tariff_id: int) -> Optional[TariffResponse]:
        tariff = await self.tariff_repo.get(tariff_id)
        if tariff:
            return TariffResponse.model_validate(tariff)
        return None

    async def get_tariff_by_name(self, name: str) -> Optional[TariffResponse]:
        tariff = await self.tariff_repo.get_by_name(name)
        if tariff:
            return TariffResponse.model_validate(tariff)
        return None

    async def list_tariffs(self, active_only: bool = True) -> List[TariffResponse]:
        if active_only:
            tariffs = await self.tariff_repo.get_active_tariffs()
        else:
            tariffs = await self.tariff_repo.list()
        return [TariffResponse.model_validate(tariff) for tariff in tariffs]

    async def update_tariff(self, tariff_id: int, tariff_data: TariffUpdate) -> Optional[TariffResponse]:
        tariff = await self.tariff_repo.get(tariff_id)
        if not tariff:
            return None

        # Проверяем уникальность имени, если оно обновляется
        if tariff_data.name and tariff_data.name != tariff.name:
            existing_tariff = await self.tariff_repo.get_by_name(tariff_data.name)
            if existing_tariff:
                raise ValueError(f"Tariff with name '{tariff_data.name}' already exists")

        update_data = tariff_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tariff, field, value)

        updated_tariff = await self.tariff_repo.update(tariff)
        return TariffResponse.model_validate(updated_tariff)

    async def deactivate_tariff(self, tariff_id: int) -> Optional[TariffResponse]:
        tariff = await self.tariff_repo.deactivate_tariff(tariff_id)
        if tariff:
            return TariffResponse.model_validate(tariff)
        return None

    async def activate_tariff(self, tariff_id: int) -> Optional[TariffResponse]:
        tariff = await self.tariff_repo.activate_tariff(tariff_id)
        if tariff:
            return TariffResponse.model_validate(tariff)
        return None

    async def delete_tariff(self, tariff_id: int) -> bool:
        return await self.tariff_repo.delete(tariff_id)