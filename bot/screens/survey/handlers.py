from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from bot.screens.startup.keyboards import startup_keyboard
from survey.runner import SurveyRunner
from utils.templates import load_template_text

from .filters import SurveyCallback
from .states import SurveyState
from .use_cases import execute_all_actions, get_survey_by_id, update_question_message

survey_router = Router()



@survey_router.callback_query(SurveyCallback.filter(F.action == "start"))
async def start_survey(query: CallbackQuery, callback_data: SurveyCallback, state: FSMContext):
    survey_id = callback_data.survey_id
    try:
        survey = await get_survey_by_id(survey_id)
    except ValueError:
        await query.answer("Опросник не найден.", show_alert=True)
        return

    runner = SurveyRunner(survey)
    runner.start()

    if not runner.current_question_id:
        await query.answer("Опросник пуст.", show_alert=True)
        return

    await state.set_state(SurveyState.current_question_id)
    await state.update_data(
        survey_id=survey_id,
        current_question_id=runner.current_question_id,
        answers=[],
        question_history=[runner.current_question_id]
    )

    await update_question_message(query, survey, runner.current_question_id)
    await query.answer()



@survey_router.callback_query(SurveyCallback.filter(F.action == "answer"), StateFilter(SurveyState))
async def handle_answer(query: CallbackQuery, callback_data: SurveyCallback, state: FSMContext):
    answer_id = callback_data.answer_id
    data = await state.get_data()

    survey_id = data['survey_id']
    current_q_id = data['current_question_id']
    answers_so_far = data.get('answers', [])
    question_history = data.get('question_history', [])
    actions_queue = data.get('actions_queue', [])

    try:
        survey = await get_survey_by_id(survey_id)
    except ValueError:
        await query.answer("Опросник не найден.", show_alert=True)
        return

    current_q = survey.get_question_by_id(current_q_id)

    selected_answer = next((a for a in current_q.answers if a.id == answer_id), None)
    if not selected_answer:
        await query.answer("Неверный ответ!", show_alert=True)
        return

    # Сохраняем ответ
    answers_so_far.append({
        "question_id": current_q_id,
        "answer_id": answer_id,
        "action": selected_answer.action
    })

    # Добавляем действие в очередь
    actions_queue.append(selected_answer.action)

    # Переход к следующему вопросу
    next_q_id = survey.get_next_question_id(current_q_id, answer_id)
    if next_q_id is None:
        await state.update_data(answers=answers_so_far, actions_queue=actions_queue)
        await execute_all_actions(query, actions_queue)
        await state.clear()
    else:
        new_history = question_history + [next_q_id]
        await state.update_data(
            current_question_id=next_q_id,
            answers=answers_so_far,
            question_history=new_history,
            actions_queue=actions_queue
        )
        is_first = len(new_history) == 1
        await update_question_message(query, survey, next_q_id, is_first)

    await query.answer()


@survey_router.callback_query(SurveyCallback.filter(F.action == "cancel"))
async def cancel_survey(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Опрос прерван.")
    await state.clear()
    await query.answer()


@survey_router.callback_query(SurveyCallback.filter(F.action == "prev"))
async def previous_question(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    survey_id = data['survey_id']
    question_history = data.get('question_history', [])
    answers_so_far = data.get('answers', [])
    actions_queue = data.get('actions_queue', [])

    if len(question_history) < 2:
        await query.message.edit_text("Невозможно вернуться к предыдущему вопросу.")
        await query.answer()
        return

    # Удаляем текущий вопрос из истории
    new_history = question_history[:-1]
    prev_q_id = new_history[-1]

    # Удаляем последний ответ и последнее действие
    new_answers = answers_so_far[:-1] if answers_so_far else []
    new_actions_queue = actions_queue[:-1] if actions_queue else []

    try:
        survey = await get_survey_by_id(survey_id)
    except ValueError:
        await query.answer("Опросник не найден.", show_alert=True)
        return

    await state.update_data(
        current_question_id=prev_q_id,
        question_history=new_history,
        answers=new_answers,
        actions_queue=new_actions_queue
    )

    await update_question_message(query, survey, prev_q_id)
    await query.answer()


@survey_router.callback_query(SurveyCallback.filter(F.action == "startup"))
async def startup_screen(query: CallbackQuery):
    text = await load_template_text("startup_menu")
    await query.message.edit_text(
        text = text,
        reply_markup = startup_keyboard()
    )
    await query.answer()



@survey_router.message(StateFilter(SurveyState.current_question_id), F.text)
async def handle_message(message: Message):
    await message.answer("Выберите вариант ответа из предложенных")