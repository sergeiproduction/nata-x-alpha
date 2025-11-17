from typing import Optional, Dict, Any
from .schemas import Survey, Question, Action, ActionType


class SurveyRunner:
    def __init__(self, survey: Survey):
        self.survey = survey
        self.current_question_id: Optional[str] = None
        self.responses: list[Dict[str, Any]] = []

    def start(self):
        if self.survey.questions:
            self.current_question_id = self.survey.questions[0].id

    async def next_question(self, answer_id: str) -> Optional[Question]:
        if not self.current_question_id:
            return None

        current_q = self.survey.get_question_by_id(self.current_question_id)
        if not current_q:
            return None

        selected_answer = next((a for a in current_q.answers if a.id == answer_id), None)
        if not selected_answer:
            raise ValueError("Invalid answer ID")

        self.responses.append({
            "question_id": self.current_question_id,
            "answer_id": answer_id,
            "action": selected_answer.action
        })

        # Выполняем действие
        await self._execute_action(selected_answer.action)

        next_qid = self.survey.get_next_question_id(self.current_question_id, answer_id)
        self.current_question_id = next_qid

        if next_qid is None:
            return None

        return self.survey.get_question_by_id(next_qid)

    async def _execute_action(self, action: Action):
        if action.type == ActionType.send_message:
            text = action.payload.get("text", "")
            print(f"[ACTION] Send message: {text}")
        elif action.type == ActionType.send_file:
            file_path = action.payload.get("file_path", "")
            print(f"[ACTION] Send file: {file_path}")

    def is_finished(self):
        return self.current_question_id is None