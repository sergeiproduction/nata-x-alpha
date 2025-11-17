import json
from typing import Any, Dict, List, Optional
from .schemas import Survey, Surveys

class SurveyManager:
    def __init__(self, surveys_file_path: str):
        self.surveys_file_path = surveys_file_path
        self.surveys_model: Surveys = None

    async def load(self):
        with open(self.surveys_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.surveys_model: Surveys = Surveys.model_validate(data)

    async def get_all_surveys(self) -> List[Dict[str, Any]]:
        if self.surveys_model is None:
            await self.load()
        return [
            {"id": sid, "title": s.title, "tags": s.tags}
            for sid, s in self.surveys_model.root.items()
        ]

    async def get_survey_by_id(self, survey_id: str) -> Optional[Survey]:
        if self.surveys_model is None:
            await self.load()
        return self.surveys_model.get_survey_by_id(survey_id)

    async def get_surveys_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        if self.surveys_model is None:
            await self.load()
        return [
            {"id": sid, "title": s.title, "tags": s.tags}
            for sid, s in self.surveys_model.root.items()
            if tag in s.tags
        ]
    
    async def get_surveys_by_tag_for_tariff(self, tag: str, user_tariff: str, tariff_name: str) -> List[Survey]:
        if self.surveys_model is None:
            await self.load()
        return [
            {"id": sid, "title": s.title, "tags": s.tags}
            for sid, s in self.surveys_model.root.items()
            if tag in s.tags and (not s.premium_only or user_tariff == tariff_name)
        ]