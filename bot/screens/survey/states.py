from aiogram.fsm.state import State, StatesGroup

class SurveyState(StatesGroup):
    current_question_id = State()
    survey_id = State()
    answers = State()