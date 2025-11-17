from aiogram.filters.callback_data import CallbackData

class SurveyCallback(CallbackData, prefix="survey"):
    action: str  # "start", "answer"
    survey_id: str = ""
    answer_id: str = ""