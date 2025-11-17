from pathlib import Path
import yaml
from bot.services.checklist import ChecklistService
from bot.services.checklist_user_item import UserChecklistItemService


async def assign_checklist_to_user(
    user_id: int,
    checklist_service: ChecklistService,
    user_checklist_item_service: UserChecklistItemService,
) -> bool:
    # Получаем все активные чек-листы
    active_checklists = await checklist_service.get_active_checklists()
    for checklist in active_checklists:
        await user_checklist_item_service.create_user_checklist_with_items(
            user_id=user_id,
            checklist_id=checklist.id,
            is_completed=False
        )
    


def create_progress_bar(done: int, total: int, width: int = 10, done_char: str = '🟩', pending_char: str = '⬛️') -> str:
    """
    Создаёт строку прогресс-бара.

    :param done: Количество выполненных элементов.
    :param total: Общее количество элементов.
    :param width: Ширина прогресс-бара в символах (по умолчанию 10).
    :param done_char: Символ для обозначения выполненной части (по умолчанию '🟩').
    :param pending_char: Символ для обозначения оставшейся части (по умолчанию '⬛️').
    :return: Строка с прогресс-баром.
    """
    if total <= 0:
        return pending_char * width

    # Ограничиваем done, чтобы не превышало total
    done = min(done, total)

    # Вычисляем процент выполнения
    percent = done / total
    # Сколько символов соответствует выполненной части
    filled = int(width * percent)
    # Оставшиеся символы — ожидаемая часть
    pending = width - filled

    bar = done_char * filled + pending_char * pending
    return bar


def load_checklist_files(path: str = "checklists"):
    checklists = []
    path_obj = Path(path)
    for file_path in path_obj.glob("*.yaml"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            checklists.append(data)
    return checklists