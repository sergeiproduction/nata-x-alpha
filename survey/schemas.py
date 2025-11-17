from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, RootModel


class ActionType(str, Enum):
    send_message = "send_message"
    send_file = "send_file"


class Action(BaseModel):
    type: ActionType
    payload: Dict[str, Any]


class Answer(BaseModel):
    id: str
    text: str
    action: Action


class Question(BaseModel):
    id: str
    text: str
    answers: List[Answer]


class Transition(BaseModel):
    from_question_id: str
    condition_answer_id: str
    to_question_id: Optional[str] = None


class Survey(BaseModel):
    title: str
    tags: List[str] = []
    premium_only: bool = False
    questions: List[Question]
    transitions: List[Transition]

    def get_question_by_id(self, qid: str) -> Optional[Question]:
        for q in self.questions:
            if q.id == qid:
                return q
        return None

    def get_next_question_id(self, current_qid: str, answer_id: str) -> Optional[str]:
        for t in self.transitions:
            if t.from_question_id == current_qid and t.condition_answer_id == answer_id:
                return t.to_question_id
        return None
    
    async def list_questions(self) -> Optional[Question]:
        return self.questions


class Surveys(RootModel[Dict[str, Survey]]):
    root: Dict[str, Survey]

    def get_survey_by_id(self, survey_id: str) -> Optional[Survey]:
        return self.root.get(survey_id)

    def get_surveys_by_tag(self, tag: str) -> List[Survey]:
        return [survey for survey in self.root.values() if tag in survey.tags]