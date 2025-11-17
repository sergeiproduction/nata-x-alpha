from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.screens.checklists.keyboards import calculate_keyboard_layout
from bot.screens.startup.filters import StartupCallback
from bot.screens.subscription.filters import PaymentCallback
from .filters import SurveyCallback




def build_main_menu_keyboard(surveys_list):
    builder = InlineKeyboardBuilder()
    for idx, item in enumerate(surveys_list):
        builder.button(
            text=f"{idx + 1}",
            callback_data=SurveyCallback(action="start", survey_id=item['id'])
        )

    layout = calculate_keyboard_layout(len(surveys_list))
    
    builder.button(
        text="Назад",
        callback_data=SurveyCallback(action="startup").pack()
    )
    
    builder.adjust(*layout)
    
    return builder.as_markup()


def build_answers_keyboard(answers, is_first_question: bool = False):
    builder = InlineKeyboardBuilder()
    for a in answers:
        builder.button(
            text=a.text,
            callback_data=SurveyCallback(action="answer", answer_id=a.id)
        )

    # Добавляем кнопку "Предыдущий вопрос" только если это не первый вопрос
    if not is_first_question:
        builder.button(
            text="Предыдущий вопрос",
            callback_data=SurveyCallback(action="prev")
        )

    builder.button(
        text="Прервать опрос",
        callback_data=SurveyCallback(action="cancel")
    )

    layout = calculate_keyboard_layout(len(answers), 2)

    if not is_first_question:
        builder.adjust(*layout, 1, 1)
    else:
        builder.adjust(*layout, 1)

    return builder.as_markup()


def payment():
    builder = InlineKeyboardBuilder()

    builder.button(text="💎Приобрести премиум", callback_data=PaymentCallback(action="show").pack()) 

    builder.button(text="◀️ Назад", callback_data=StartupCallback(action="back").pack())
    builder.adjust(1,1)
    return builder.as_markup()