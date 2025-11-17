from datetime import datetime
from dateutil.relativedelta import relativedelta
from .base import ReportGenerator



class USNDeclarationGenerator(ReportGenerator):
    """
    Генератор отчета: Декларация по УСН.
    Годовой отчет для упрощенной системы налогообложения.
    Сдается до 25 марта года, следующего за отчетным.
    """
    def generate_report_name(self) -> str:
        return "Декларация по УСН"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - год, заканчивается 31.12.2024, дата сдачи - до 25.03.2025
        # Берем год из даты периода и устанавливаем 25 марта следующего года
        return datetime(period_end_date.year + 1, 3, 25)


class AccountingReportGenerator(ReportGenerator):
    """
    Генератор отчета: Бухгалтерская отчетность.
    Годовая бухгалтерская отчетность, сдается в электронном виде.
    Сдается до 31 марта года, следующего за отчетным.
    """
    def generate_report_name(self) -> str:
        return "Бухгалтерская отчетность"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - год, заканчивается 31.12.2024, дата сдачи - до 31.03.2025
        return datetime(period_end_date.year + 1, 3, 31)


class OVEDConfirmationGenerator(ReportGenerator):
    """
    Генератор отчета: Подтверждение ОВЭД.
    Отчет о подтверждении основного вида экономической деятельности (до 2025 года).
    Сдается до 15 апреля года, следующего за отчетным.
    """
    def generate_report_name(self) -> str:
        return "Подтверждение ОВЭД"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - год, заканчивается 31.12.2024, дата сдачи - до 15.04.2025
        return datetime(period_end_date.year + 1, 4, 15)


class Form6Generator(ReportGenerator):
    """
    Генератор отчета: Форма № 6.
    Сведения о воинском учете (для военкомата).
    Сдается до 15 сентября года, следующего за отчетным.
    """
    def generate_report_name(self) -> str:
        return "Форма № 6"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - год, заканчивается 31.12.2024, дата сдачи - до 15.09.2025
        return datetime(period_end_date.year + 1, 9, 15)


class Form18Generator(ReportGenerator):
    """
    Генератор отчета: Форма № 18.
    Сведения о среднесписочной численности работников (для военкомата).
    Сдается до 15 сентября года, следующего за отчетным.
    """
    def generate_report_name(self) -> str:
        return "Форма № 18"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - год, заканчивается 31.12.2024, дата сдачи - до 15.09.2025
        return datetime(period_end_date.year + 1, 9, 15)


class Form19Generator(ReportGenerator):
    """
    Генератор отчета: Форма № 19.
    Сведения о лицах, подлежащих призыву на военную службу (для военкомата).
    Сдается до 15 сентября года, следующего за отчетным.
    """
    def generate_report_name(self) -> str:
        return "Форма № 19"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - год, заканчивается 31.12.2024, дата сдачи - до 15.09.2025
        return datetime(period_end_date.year + 1, 9, 15)


class ENPNotificationGenerator(ReportGenerator):
    """
    Генератор отчета: Уведомление о налогах для ЕНП.
    Уведомление о применении специального налогового режима "Налог на профессиональный доход".
    Сдается до 25-го числа месяца, следующего за отчетным кварталом.
    """
    def generate_report_name(self) -> str:
        return "Уведомление о налогах для ЕНП"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - квартал, заканчивается 31.03.2025, дата сдачи - до 25.04.2025
        # Берем дату окончания квартала и устанавливаем 25-е число следующего месяца
        next_month = period_end_date + relativedelta(months=1)
        return datetime(next_month.year, next_month.month, 25)


class NDFL6Generator(ReportGenerator):
    """
    Генератор отчета: 6-НДФЛ.
    Сведения о доходах физических лиц за отчетный период (квартал).
    Сдается до 25-го числа месяца, следующего за отчетным кварталом.
    """
    def generate_report_name(self) -> str:
        return "6-НДФЛ"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - квартал, заканчивается 31.03.2025, дата сдачи - до 25.04.2025
        # Берем дату окончания квартала и устанавливаем 25-е число следующего месяца
        next_month = period_end_date + relativedelta(months=1)
        return datetime(next_month.year, next_month.month, 25)


class InsuranceContributionReportGenerator(ReportGenerator):
    """
    Генератор отчета: Расчет по страховым взносам (РСВ).
    Сведения о суммах страховых взносов за отчетный период (квартал).
    Сдается до 25-го числа месяца, следующего за отчетным кварталом.
    """
    def generate_report_name(self) -> str:
        return "Расчет по страховым взносам (РСВ)"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - квартал, заканчивается 31.03.2025, дата сдачи - до 25.04.2025
        # Берем дату окончания квартала и устанавливаем 25-е число следующего месяца
        next_month = period_end_date + relativedelta(months=1)
        return datetime(next_month.year, next_month.month, 25)


class EFS1Generator(ReportGenerator):
    """
    Генератор отчета: ЕФС-1.
    Единый расчет по страховым взносам (до 2021 года, заменен РСВ).
    (Возможно, устаревший генератор, в зависимости от контекста create_usn)
    Сдается до 25-го числа месяца, следующего за отчетным кварталом.
    """
    def generate_report_name(self) -> str:
        return "ЕФС-1"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - квартал, заканчивается 31.03.2025, дата сдачи - до 25.04.2025
        # Берем дату окончания квартала и устанавливаем 25-е число следующего месяца
        next_month = period_end_date + relativedelta(months=1)
        return datetime(next_month.year, next_month.month, 25)


class PSVGenerator(ReportGenerator):
    """
    Генератор отчета: Персонифицированные сведения (ПСВ).
    Сведения о застрахованных лицах (ежемесячно).
    Сдается до 25-го числа месяца, следующего за отчетным месяцем.
    """
    def generate_report_name(self) -> str:
        return "Персонифицированные сведения (ПСВ)"

    def calculate_deadline(self, period_end_date: datetime) -> datetime:
        # Период - месяц, заканчивается 31.01.2025, дата сдачи - до 25.02.2025
        # Берем дату окончания месяца и устанавливаем 25-е число следующего месяца
        next_month = period_end_date + relativedelta(months=1)
        return datetime(next_month.year, next_month.month, 25)