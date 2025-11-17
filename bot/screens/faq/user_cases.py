import json
from typing import Any, Dict, Optional
import pymorphy2

from faq.manager import FaqManager

morph = pymorphy2.MorphAnalyzer()

async def decline_to_dative(word: str) -> str:
    """
    Склоняет существительное в дательный падеж (кому? чему?).

    :param word: Слово в именительном падеже (например, "Положение", "Договор").
    :return: Слово в дательном падеже (например, "Положению", "Договору").
    """
    parsed = morph.parse(word)[0]
    declined = parsed.inflect({'datv'})  # дательный падеж
    return declined.word if declined else word


def get_faq_data_for_context(path: str = "./storage/faq.json") -> Dict[str, Any]:
    """
    Возвращает словарь с информацией по FAQ для использования в локальном/глобальном контексте.
    Содержит только уникальные формулировки вопросов (без ответов, пояснений, категорий и разделов).
    """
    with open(path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    faq_info = set()  # Используем set для уникальности

    # Обрабатываем все категории
    for _, category_data in raw_data.items():
        # Пропускаем "items" на верхнем уровне, если есть
        sections = category_data.get("sections", {})
        
        # Обрабатываем разделы
        for section_name, section_data in sections.items():
            section_items = section_data.get("items", [])
            
            for item in section_items:
                question = item.get("question", "")
                # Пропускаем "answer" и "explanation"
                if question:
                    faq_info.add(question)  # set автоматически удаляет дубликаты

    # Преобразуем set в list и возвращаем в нужном формате: {"faq": [...]}
    return {"faq": list(faq_info)}


async def find_faq_section_by_question(search_term: str, path: str = "./storage/faq.json") -> Optional[Dict[str, Any]]:
    """
    Находит секцию FAQ, к которой относится вопрос, содержащий поисковый термин.
    """
    faq_manager = FaqManager(path)
    await faq_manager.load_data()

    result = await faq_manager.find_item_by_question(search_term)
    
    if result:
        return {
            "category": result["category"],
            "section": result["section"],
            "item": result["item"]
        }
    
    return None