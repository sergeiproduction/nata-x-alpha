from typing import Dict, List, Optional
from pydantic import BaseModel, Field, RootModel


class FaqItem(BaseModel):
    """
    Pydantic-модель для одного элемента FAQ.
    """
    question: str
    answer: str
    explanation: Optional[str] = ""


class FaqSection(BaseModel):
    """
    Pydantic-модель для раздела внутри категории FAQ.
    """
    items: List[FaqItem]


class FaqCategory(BaseModel):
    """
    Pydantic-модель для категории FAQ.
    Может содержать элементы на уровне категории и разделы.
    """
    items: List[FaqItem] = []  # Элементы на уровне категории (опционально)
    sections: Dict[str, FaqSection] = {}  # Разделы внутри категории (опционально)



class FaqData(RootModel[Dict[str, FaqCategory]]):
    """
    Pydantic-модель для всей структуры FAQ.
    """
    root: Dict[str, FaqCategory] = Field(default_factory=dict)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __setitem__(self, key, value):
        self.root[key] = value

    def __contains__(self, item):
        return item in self.root