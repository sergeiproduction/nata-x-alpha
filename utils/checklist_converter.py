from bot.services.checklist import ChecklistService
from bot.services.checklist_item import ChecklistItemService
from schemas.checklist import ChecklistCreate
from schemas.checklist_item import ChecklistItemCreate
import yaml


async def create_checklists_from_yaml_data(
    yaml_file_path: str,
    checklist_service: ChecklistService,
    checklist_item_service: ChecklistItemService
):
    """
    Создает чек-листы из YAML файла
    """
    with open(yaml_file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
    checklists_data: dict = data

    name = checklists_data.get("name")
    description = checklists_data.get("description")
    
    # Создаем чек-лист
    checklist_create = ChecklistCreate(
        name=name,
        description=description,
        is_active=True
    )

    created_checklist = await checklist_service.create_checklist(checklist_create)
    
    if created_checklist:
        # Создаем элементы чек-листа
        for item in checklists_data.get("items"):
            item_create = ChecklistItemCreate(
                checklist_id=created_checklist.id,
                content=item
            )
            await checklist_item_service.create_checklist_item(item_create)