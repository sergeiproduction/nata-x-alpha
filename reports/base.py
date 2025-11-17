from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json


class ReportGenerator(ABC):
    """
    Абстрактный класс генератора отчетов для государственных органов.
    """

    def __init__(self, submission_date: datetime, period_date: datetime, instance: str):
        """
        Инициализирует генератор отчета.

        :param submission_date: Дата сдачи отчета.
        :param period_date: Дата (период), за которую подается отчет.
        :param instance: Организация или инстанция, куда сдается отчетность (например, "ФНС", "СФР").
        """
        self.submission_date = submission_date
        self.period_date = period_date
        self.instance = instance

    @abstractmethod
    def generate_report_name(self) -> str:
        """
        Абстрактный метод для генерации названия отчета.
        Должен быть реализован в подклассах.

        :return: Название отчета.
        """
        pass

    @abstractmethod
    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        """
        Абстрактный метод для вычисления даты сдачи отчета на основе даты окончания отчетного периода.
        Должен быть реализован в подклассах.

        :param period_end_date: Дата окончания отчетного периода.
        :return: Вычисленная дата сдачи отчета.
        """
        pass

    def save_to_json(self, file_path: str):
        """
        Сохраняет отчет в JSON-файл в заданном формате.
        """
        report_name = self.generate_report_name()

        # Структура отчета включает название, дату сдачи, период сдачи и инстанцию
        report_structure = {
            report_name: {
                "Дата сдачи": self.submission_date.isoformat(),
                "Период сдачи": self.period_date.isoformat(),
                "Инстанция": self.instance
            }
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_structure, f, ensure_ascii=False, indent=4)

    def adjust_date_for_weekend(self, date_obj: datetime) -> datetime:
        """
        Корректирует дату, если она выпадает на выходной день (суббота или воскресенье),
        перенося на следующий понедельник.

        :param date_obj: Исходная дата.
        :return: Скорректированная дата (если нужно).
        """
        # date.weekday() возвращает 0 для понедельника, 5 для субботы, 6 для воскресенья
        if date_obj.weekday() >= 5:  # 5 = Суббота, 6 = Воскресенье
            days_to_add = 7 - date_obj.weekday() # 7 - 5 = 2 (до понедельника)
            if date_obj.weekday() == 6: # Если воскресенье, добавляем 1 день до понедельника
                days_to_add = 1
            return date_obj + timedelta(days=days_to_add)
        return date_obj