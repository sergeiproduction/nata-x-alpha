from typing import List, Optional, Tuple

from faq.schemas import FaqItem


class FAQIterator:
    def __init__(self, items: List[FaqItem]):
        self.items = items
        self.current_index = -1  # начинаем с -1, чтобы first() или next() давали 0

    async def has_next(self) -> bool:
        """Проверяет, есть ли следующий элемент."""
        return len(self.items) > 0

    async def next(self) -> Optional[Tuple[FaqItem, int]]:
        """
        Возвращает следующий элемент и его индекс.
        Если список пуст, возвращает None.
        Если текущий индекс был последним, возвращается первый элемент (зацикливание).
        """
        if not self.items:
            return None

        self.current_index = (self.current_index + 1) % len(self.items)
        current_item = self.items[self.current_index]
        return current_item, self.current_index

    async def prev(self) -> Optional[Tuple[FaqItem, int]]:
        """
        Возвращает предыдущий элемент и его индекс.
        Если список пуст или текущий индекс — первый, возвращается последний элемент (зацикливание).
        """
        if not self.items:
            return None

        prev_index = (self.current_index - 1) % len(self.items)
        self.current_index = prev_index
        current_item = self.items[self.current_index]
        return current_item, self.current_index


    async def current(self) -> Optional[Tuple[FaqItem, int]]:
        """
        Возвращает текущий элемент и его индекс.
        """
        if not self.items or self.current_index < 0:
            return None

        current_item = self.items[self.current_index]
        return current_item, self.current_index

    async def reset(self):
        """
        Сбрасывает текущий индекс на -1.
        """
        self.current_index = -1

    async def get_by_index(self, index: int) -> Optional[Tuple[FaqItem, int]]:
        """
        Возвращает элемент по индексу.
        """
        if 0 <= index < len(self.items):
            self.current_index = index
            item = self.items[index]
            return item, index
        return None