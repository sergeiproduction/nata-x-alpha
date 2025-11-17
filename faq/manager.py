import json
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import ValidationError
from .schemas import FaqCategory, FaqData, FaqItem


class FaqManager:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data: Optional[FaqData] = None

    async def load_data(self):
        """
        Асинхронно загружает данные из файла и валидирует их.
        """
        try:
            async with aiofiles.open(self.file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            self.data = FaqData.model_validate(data)
        except FileNotFoundError:
            print(f"Файл {self.file_path} не найден. Создается пустая структура.")
            self.data = FaqData(__root__={})
        except ValidationError as e:
            print(f"Ошибка валидации Pydantic: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            raise

    async def save_data(self):
        """
        Асинхронно сохраняет текущие данные в файл.
        """
        if self.data is not None:
            try:
                data_to_write = self.data.model_dump()
                json_string = json.dumps(data_to_write, ensure_ascii=False, indent=2)
                async with aiofiles.open(self.file_path, 'w', encoding='utf-8') as f:
                    await f.write(json_string)
            except Exception as e:
                print(f"Ошибка при записи в файл: {e}")
                raise
        else:
            print("Нет данных для сохранения.")

    async def get_categories(self) -> List[str]:
        """
        Асинхронно возвращает список всех названий категорий.
        """
        if not self.data:
            return []
        return list(self.data.root.keys())  # Изменено на .root

    async def get_items_by_category(self, category_name: str) -> List[FaqItem]:
        """
        Асинхронно возвращает список элементов FAQ для указанной категории (верхнего уровня).
        """
        if not self.data or category_name not in self.data.root:  # Изменено на .root
            return []
        return self.data.root[category_name].items  # Изменено на .root

    async def get_sections_by_category(self, category_name: str) -> List[str]:
        """
        Асинхронно возвращает список названий разделов в указанной категории.
        """
        if not self.data or category_name not in self.data.root:  # Изменено на .root
            return []
        return list(self.data.root[category_name].sections.keys())  # Изменено на .root

    async def get_items_by_section(self, category_name: str, section_name: str) -> List[FaqItem]:
        """
        Асинхронно возвращает список элементов FAQ для указанного раздела в категории.
        """
        if not self.data or category_name not in self.data.root:  # Изменено на .root
            return []
        category = self.data.root[category_name]  # Изменено на .root
        if section_name not in category.sections:
            return []
        return category.sections[section_name].items

    async def find_item_by_question(self, search_term: str, category_filter: Optional[str] = None, section_filter: Optional[str] = None) -> Optional[Dict[str, any]]:
        """
        Асинхронно находит элемент FAQ по части вопроса.
        Можно ограничить поиск по категории и/или разделу.
        """
        if not self.data:
            return None

        categories_to_search = [category_filter] if category_filter else await self.get_categories()

        for cat_name in categories_to_search:
            cat = self.data.root[cat_name]

            # Поиск в элементах категории
            if not section_filter:
                for item in cat.items:
                    if search_term.lower() in item.question.lower():
                        return {"category": cat_name, "section": None, "item": item}

            # Поиск в разделах
            sections_to_search = [section_filter] if section_filter else await self.get_sections_by_category(cat_name)
            for sec_name in sections_to_search:
                if sec_name in cat.sections:
                    for item in cat.sections[sec_name].items:
                        if search_term.lower() in item.question.lower():
                            return {"category": cat_name, "section": sec_name, "item": item}
        return None

    async def add_item(self, category_name: str, item: FaqItem, section_name: Optional[str] = None):
        """
        Асинхронно добавляет новый FaqItem в указанную категорию и, при необходимости, в указанный раздел.
        Если категории или раздела не существует, они будут созданы.
        """
        if not self.data:
            await self.load_data()

        # Проверяем, существует ли категория
        if category_name not in self.data.root:
            self.data.root[category_name] = FaqCategory(items=[], sections={})

        category = self.data.root[category_name]

        if section_name:
            if section_name not in category.sections:
                category.sections[section_name] = {"items": []}
            self.data.root[category_name].sections[section_name]["items"].append(item)
        else:
            self.data.root[category_name].items.append(item)