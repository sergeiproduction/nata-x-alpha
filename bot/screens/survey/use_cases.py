import json
import os
from typing import TYPE_CHECKING, Any, Dict

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaDocument, FSInputFile, Message 

from bot.screens.survey.keyboards import build_answers_keyboard, payment
from bot.screens.survey.states import SurveyState
from schemas.user import User
from survey.manager import SurveyManager
from survey.runner import SurveyRunner
from survey.schemas import ActionType, Question, Survey


from utils.templates import load_template_text
from neural import processor

if TYPE_CHECKING:
    from survey import SurveyManager


async def get_survey_by_id(survey_id: str) -> Survey:
    manager = SurveyManager("./storage/surveys.json")
    survey_dict = await manager.get_survey_by_id(survey_id)
    if not survey_dict:
        raise ValueError("Опросник не найден.")
    return Survey.model_validate(survey_dict)



async def execute_all_actions(query: CallbackQuery, actions_queue):
    messages = []
    files_to_attach = []

    for _, action in enumerate(actions_queue):
        if action.type == ActionType.send_message:
            text = action.payload.get("text", "")
            if isinstance(text, list):
                text = '\n'.join(text)
            if text.strip():  # Проверяем, что текст не пустой
                messages.append(text)
        elif action.type == ActionType.send_file:
            file_path = action.payload.get("file_path", "")
            if file_path:
                # Проверяем, существует ли файл
                if os.path.exists(file_path):
                    # Используем FSInputFile для локальных файлов
                    input_file = FSInputFile(file_path)
                    files_to_attach.append(InputMediaDocument(media=input_file))
                else:
                    # Если файл не найден, добавляем сообщение об ошибке
                    messages.append(f"[Файл не найден: {file_path}]")

    # Если нет сообщений и файлов, возвращаем к выбору этапа
    if not messages and not files_to_attach:
        await query.message.edit_text("Все рекомендации пустые. Выберите следующий этап:")
        await query.answer()
        return

    if messages:
        full_text = await load_template_text("survey_result", messages=messages)
        await query.message.answer(full_text)

    if files_to_attach:
        await query.message.answer_media_group(files_to_attach)



async def update_question_message(query: CallbackQuery, survey: Survey, question_id: str, is_first_question=True):
    question = survey.get_question_by_id(question_id)
    if not question:
        raise ValueError("Вопрос не найден.")
    await query.message.edit_text(question.text, reply_markup=build_answers_keyboard(question.answers, is_first_question))



def get_survey_data_for_context(path: str = "./storage/surveys.json") -> Dict[str, Any]:
    """
    Возвращает словарь с информацией по всем опросникам для использования в глобальном контексте.
    """
    
    with open(path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    surveys_info = {}

    # Пробуем разные возможные структуры
    root_data = raw_data.get("root") or raw_data.get("surveys") or raw_data

    if isinstance(root_data, dict):
        for survey_id, survey_data in root_data.items():
            if isinstance(survey_data, dict):
                surveys_info[survey_id] = {
                    "title": survey_data.get("title", ""),
                    "premium_only": survey_data.get("premium_only", False),
                    "tags": survey_data.get("tags", [])
                }
    elif isinstance(root_data, list):
        for i, survey_data in enumerate(root_data):
            if isinstance(survey_data, dict):
                survey_id = survey_data.get("id") or f"survey_{i}"
                surveys_info[survey_id] = {
                    "title": survey_data.get("title", ""),
                    "premium_only": survey_data.get("premium_only", False),
                    "tags": survey_data.get("tags", [])
                }

    return {"surveys": surveys_info}



@processor.register(description="Выбирает подходящий опросник из словаря, основываясь на названии из базы на английском", storage_args=["state", "message", "user"])
async def route_survey(survey_name: str, state: FSMContext, message: Message, user: User):
    
    survey = await get_survey_by_id(survey_name)

    if not user.is_premium and survey.premium_only:
        await message.answer("Для доступа к персональной рекомендации по данной теме приобретите премиум", reply_markup=payment())
        return

    runner = SurveyRunner(survey)
    runner.start()

    if not runner.current_question_id:
        return

    await state.set_state(SurveyState.current_question_id)
    await state.update_data(
        survey_id=survey_name,
        current_question_id=runner.current_question_id,
        answers=[],
        question_history=[runner.current_question_id]
    )

    questions = await survey.list_questions()
    first_question: Question = questions[0]
    await message.answer(first_question.text, reply_markup=build_answers_keyboard(first_question.answers, True))