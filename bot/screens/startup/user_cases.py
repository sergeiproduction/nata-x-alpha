from typing import List
from aiogram.types import CallbackQuery

from bot.screens.checklists.user_cases import load_checklist_files
from bot.screens.survey.keyboards import build_main_menu_keyboard
from bot.services.checklist import ChecklistService
from bot.services.checklist_item import ChecklistItemService
from bot.services.checklist_user_item import UserChecklistItemService
from bot.services.user_subscription import UserSubscriptionService
from schemas.checklist import ChecklistCreate
from schemas.checklist_item import ChecklistItemCreate
from schemas.user import UserResponse
from survey.manager import SurveyManager
from utils.templates import load_template_text



async def handle_stage_request(
    message_or_query,
    user: UserResponse,
    user_subscription_service: UserSubscriptionService,
    stage_tag: str
) -> None:
    """
    Общая логика обработки запроса на отображение опросников для указанного этапа.

    :param message_or_query: Может быть Message или CallbackQuery.
    :param user: Объект пользователя.
    :param user_subscription_service: Сервис для работы с подписками пользователя.
    :param stage_tag: Тег этапа, например "I этап".
    """
    # 1. Получение подписки
    subscription = await user_subscription_service.get_active_subscription(user.id)

    # 2. Инициализация SurveyManager
    survey_manager = SurveyManager("./storage/surveys.json")

    # 3. Получение доступных опросников для тарифа пользователя
    surveys = await survey_manager.get_surveys_by_tag_for_tariff(
        stage_tag, subscription.tariff_name, "premium"
    )

    # 4. Проверка наличия опросников
    if not surveys:
        text = f"Нет доступных опросников для {stage_tag}."
        if isinstance(message_or_query, CallbackQuery):
            await message_or_query.message.edit_text(text)
            await message_or_query.answer()
        else:
            await message_or_query.answer(text)
        return

    # 5. Подготовка данных опросников с индексами
    surveys_with_index = [
        {"index": idx + 1, "id": s["id"], "title": s["title"], "tags": s["tags"]}
        for idx, s in enumerate(surveys)
    ]

    # 6. Получение всех опросников и определение премиум-опросников, недоступных пользователю
    all_surveys = survey_manager.surveys_model.root
    premium_surveys = [
        {"title": s.title}
        for _, s in all_surveys.items()
        if stage_tag in s.tags and s.premium_only and subscription.tariff_name != "premium"
    ]

    # 7. Построение клавиатуры
    keyboard = build_main_menu_keyboard(surveys)

    # 8. Загрузка и рендеринг текста шаблона
    text = await load_template_text(
        "survey_item",
        surveys=surveys_with_index,
        premium_surveys=premium_surveys,
        has_premium_access=subscription.tariff_name == "premium"
    )

    # 9. Отправка/обновление сообщения
    if isinstance(message_or_query, CallbackQuery):
        await message_or_query.message.edit_text(text, reply_markup=keyboard)
        await message_or_query.answer()
    else:
        await message_or_query.answer(text, reply_markup=keyboard)

    

async def get_checklists(
    checklist_service: ChecklistService,
    checklist_item_service: ChecklistItemService,
    user_checklist_item_service: UserChecklistItemService,
    user: UserResponse
) -> List[dict]: # Возвращаем список чек-листов для дальнейшего использования
    """
    Общая логика: загрузка чек-листов из YAML, синхронизация с БД,
    создание пользовательских элементов чек-листа.
    """
    checklist_data_list = load_checklist_files()

    for checklist_data in checklist_data_list:
        # Создаём чек-лист
        checklist_create = ChecklistCreate(
            name=checklist_data["name"],
            description=checklist_data["description"],
            is_active=True
        )
        checklist_response = await checklist_service.create_checklist(checklist_create)

        # Проверим, были ли уже созданы элементы
        existing_items = await checklist_item_service.get_checklist_items(checklist_response.id)
        if not existing_items:
            # Создаём элементы
            for item_content in checklist_data["items"]:
                item_create = ChecklistItemCreate(
                    checklist_id=checklist_response.id,
                    content=item_content
                )
                await checklist_item_service.create_checklist_item(item_create)

        # Создаём пользовательские элементы чек-листа
        await user_checklist_item_service.create_user_checklist_with_items(
            user_id=user.id,
            checklist_id=checklist_response.id,
            is_completed=False
        )
    
    # Возвращаем активные чек-листы для отображения
    return await checklist_service.get_active_checklists()