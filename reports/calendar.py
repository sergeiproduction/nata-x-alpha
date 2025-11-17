from datetime import datetime
import json
from typing import Dict, List
from .base import ReportGenerator
from dateutil.relativedelta import relativedelta


class ReportCalendar:
    """
    Класс для создания календаря отчетов.
    """

    def __init__(self):
        self.reports: List[Dict[str, str]] = [] # Теперь список

    def add_report_generator(self, generator: ReportGenerator, n_periods: int, period_unit: str = 'month'):
        """
        Добавляет генератор отчета в календарь и генерирует для него N отчетов.
        :param generator: Экземпляр ReportGenerator.
        :param n_periods: Количество периодов для генерации.
        :param period_unit: Единица измерения периода ('month', 'year', 'quarter').
        """
        if period_unit not in ['month', 'year', 'quarter']:
             raise ValueError(f"Неподдерживаемая единица периода: {period_unit}. Допустимые значения: 'month', 'year', 'quarter'.")

        report_name = generator.generate_report_name()

        for i in range(n_periods):
            if period_unit == 'month':
                delta = relativedelta(months=i)
            elif period_unit == 'year':
                delta = relativedelta(years=i)
            elif period_unit == 'quarter':
                delta = relativedelta(months=i * 3)

            # Вычисляем дату окончания периода
            new_period_date = generator.period_date + delta
            
            # Вычисляем дату сдачи с помощью метода calculate_deadline
            calculated_deadline = generator.calculate_deadline(new_period_date)
            
            # Корректируем дату сдачи, если она выпадает на выходной
            adjusted_submission_date = generator.adjust_date_for_weekend(calculated_deadline)

            report_entry = {
                "Название": report_name,
                "Дата сдачи": adjusted_submission_date.strftime("%d.%m.%Y"), # Изменен формат: день.месяц.год
                "Период сдачи": self._format_period(new_period_date, period_unit), # Используем новую функцию
                "Инстанция": generator.instance # Добавляем инстанцию
            }
            # Добавляем запись в общий список
            self.reports.append(report_entry)

    def _format_period(self, date_obj: datetime, period_unit: str) -> str:
        """
        Форматирует период в зависимости от единицы измерения.
        :param date_obj: Дата периода.
        :param period_unit: Единица измерения ('month', 'year', 'quarter').
        :return: Строка с отформатированным периодом.
        """
        if period_unit == 'month':
            # мес. год (например, 03.2023)
            return f"{date_obj.month:02d}.{date_obj.year}"
        elif period_unit == 'year':
            # год (например, 2023)
            return f"{date_obj.year}"
        elif period_unit == 'quarter':
            # I-IV квартал. год (например, I кв. 2023)
            quarter = (date_obj.month - 1) // 3 + 1
            quarter_str = {1: "I", 2: "II", 3: "III", 4: "IV"}[quarter]
            return f"{quarter_str} кв. {date_obj.year}"
        else:
            # На всякий случай, если передадут что-то другое
            return date_obj.strftime("%Y-%m-%d")


    def save_calendar_to_json(self, file_path: str):
        """
        Сохраняет календарь отчетов в JSON-файл.
        :param file_path: Путь к файлу календаря.
        """
        # Сортируем по дате сдачи перед сохранением
        self.reports.sort(key=lambda x: datetime.strptime(x["Дата сдачи"], "%d.%m.%Y"))
        
        # Структура календаря - просто список отсортированных отчетов
        calendar_structure = self.reports

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(calendar_structure, f, ensure_ascii=False, indent=4)

    def load_calendar_from_json(self, file_path: str):
        """
        Загружает календарь отчетов из JSON-файла.
        :param file_path: Путь к файлу календаря.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.reports = json.load(f)

    def get_reports_for_date(self, target_date: datetime) -> List[Dict[str, str]]:
        """
        Возвращает список отчетов, дата сдачи которых совпадает с указанной датой.
        :param target_date: Дата, для которой нужно найти отчеты (формат: день.месяц.год).
        :return: Список отчетов.
        """
        target_date_str = target_date.strftime("%d.%m.%Y")
        filtered_reports = [report for report in self.reports if report["Дата сдачи"] == target_date_str]
        return filtered_reports