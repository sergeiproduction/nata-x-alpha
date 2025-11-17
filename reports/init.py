# --- Пример использования ---
from datetime import datetime

from reports.calendar import ReportCalendar
from reports.reports import AccountingReportGenerator, EFS1Generator, ENPNotificationGenerator, Form18Generator, Form19Generator, Form6Generator, InsuranceContributionReportGenerator, NDFL6Generator, OVEDConfirmationGenerator, PSVGenerator, USNDeclarationGenerator


if __name__ == "__main__":
    # Данные для примера: начальные даты
    # Пусть начальная дата сдачи будет в субботу (2025-01-04), для проверки корректировки
    # Период - конец января 2025
    year = 2025
    initial_sub_date = datetime(year, 1, 1) # Суббота, 4 января 2025
    initial_per_date = datetime(year, 1, 31) # Пятница, 31 января 2025

    # Создаем календарь
    calendar = ReportCalendar()

    # 1. Добавляем в календарь 2 отчета "Декларация по УСН" (ежегодно) - инстанция "ФНС"
    usn_gen = USNDeclarationGenerator(initial_sub_date, initial_per_date, instance="ФНС")
    calendar.add_report_generator(usn_gen, n_periods=10, period_unit='year')

    # 2. Добавляем в календарь 4 отчета "Подтверждение ОВЭД" (ежеквартально) - инстанция "СФР"
    oved_gen = OVEDConfirmationGenerator(initial_sub_date, initial_per_date, instance="СФР")
    calendar.add_report_generator(oved_gen, n_periods=40, period_unit='quarter')

    # 3. Добавляем в календарь 2 отчета "Бухгалтерская отчетность" (ежегодно) - инстанция "ФНС"
    acc_gen = AccountingReportGenerator(initial_sub_date, initial_per_date, instance="ФНС")
    calendar.add_report_generator(acc_gen, n_periods=10, period_unit='year')

    # 4. Добавляем в календарь 2 отчета "Форма № 6" (ежегодно) - инстанция "Военкомат"
    form6_gen = Form6Generator(initial_sub_date, initial_per_date, instance="Военкомат")
    calendar.add_report_generator(form6_gen, n_periods=10, period_unit='year')

    # 5. Добавляем в календарь 2 отчета "Форма № 18" (ежегодно) - инстанция "Военкомат"
    form18_gen = Form18Generator(initial_sub_date, initial_per_date, instance="Военкомат")
    calendar.add_report_generator(form18_gen, n_periods=10, period_unit='year')

    # 6. Добавляем в календарь 2 отчета "Форма № 19" (ежегодно) - инстанция "Военкомат"
    form19_gen = Form19Generator(initial_sub_date, initial_per_date, instance="Военкомат")
    calendar.add_report_generator(form19_gen, n_periods=10, period_unit='year')

    # 7. Добавляем в календарь 4 отчета "Уведомление о налогах для ЕНП" (ежеквартально) - инстанция "ФНС"
    enp_gen = ENPNotificationGenerator(initial_sub_date, initial_per_date, instance="ФНС")
    calendar.add_report_generator(enp_gen, n_periods=40, period_unit='quarter')

    # 8. Добавляем в календарь 4 отчета "6-НДФЛ" (ежеквартально) - инстанция "ФНС"
    ndfl_gen = NDFL6Generator(initial_sub_date, initial_per_date, instance="ФНС")
    calendar.add_report_generator(ndfl_gen, n_periods=40, period_unit='quarter')

    # 9. Добавляем в календарь 4 отчета "Расчет по страховым взносам (РСВ)" (ежеквартально) - инстанция "ФНС"
    rsv_gen = InsuranceContributionReportGenerator(initial_sub_date, initial_per_date, instance="ФНС")
    calendar.add_report_generator(rsv_gen, n_periods=40, period_unit='quarter')

    # 10. Добавляем в календарь 4 отчета "ЕФС-1" (ежеквартально) - инстанция "СФР"
    efs_gen = EFS1Generator(initial_sub_date, initial_per_date, instance="СФР")
    calendar.add_report_generator(efs_gen, n_periods=40, period_unit='quarter')

    # 11. Добавляем в календарь 12 отчетов "Персонифицированные сведения (ПСВ)" (ежемесячно) - инстанция "ФНС"
    psv_gen = PSVGenerator(initial_sub_date, initial_per_date, instance="ФНС")
    calendar.add_report_generator(psv_gen, n_periods=120, period_unit='month')

    # Сохраняем общий календарь
    calendar.save_calendar_to_json("report_calendar.json")