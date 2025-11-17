from collections import defaultdict
from bot.services.notification_type import NotificationTypeService
from bot.services.user_notification import UserNotificationService
from reports.calendar import ReportCalendar
from schemas.user_notification import UserNotificationUpdate

from datetime import datetime, timedelta

from utils.templates import load_template_text

async def update_notification_settings(user_id: int, notification_name: str, 
                                        notification_type_service: NotificationTypeService,
                                        user_notification_service: UserNotificationService
):  
    notification_type = await notification_type_service.get_notification_type_by_name(notification_name)
    notification_status = await user_notification_service.get_user_notification(user_id, notification_type.id)

    await user_notification_service.update_user_notification(
        user_id,
        notification_type.id,
        UserNotificationUpdate(is_active=not notification_status.is_active)
    )


async def show_report_ahead(days: int = 1) -> str:
    # Получаем последний день текущего месяца (дата отсечки)
    now = datetime.now()
    # Устанавливаем день на 1 и добавляем месяц, затем вычитаем 1 день
    cutoff_date = now.date() + timedelta(days=days)
    
    print("CUTOFF: ", cutoff_date)
    # Создаем экземпляр календаря
    calendar = ReportCalendar()
    
    # Загружаем данные из файла (предполагается, что файл существует)
    calendar.load_calendar_from_json("./storage/report_calendar.json")
    
    # Получаем все отчеты из календаря
    all_reports = calendar.reports
    
    # Фильтруем отчеты по диапазону дат [текущая дата; дата отсечки]
    current_date = now.date()
    cutoff_date_obj = cutoff_date
    
    filtered_reports = []
    for report in all_reports:
        report_date_obj = datetime.strptime(report["Дата сдачи"], "%d.%m.%Y").date()
        if current_date <= report_date_obj <= cutoff_date_obj:
            filtered_reports.append(report)
    
    # Сортировка по дате сдачи
    filtered_reports.sort(key=lambda x: datetime.strptime(x["Дата сдачи"], "%d.%m.%Y"))
    
    # Группировка по дате и инстанциям
    grouped_by_date = defaultdict(lambda: defaultdict(list))
    for report in filtered_reports:
        grouped_by_date[report['Дата сдачи']][report['Инстанция']].append(report)
    
    # Формируем данные для шаблона
    template_data = {
        "is_month_calendar": True,  # Это календарь на месяц
        "dates": []
    }

    if filtered_reports:
        # Добавляем иконки для инстанций
        instance_icons = {
            "ФНС": "🏛️",
            "СФР": "👥",
            "Военкомат": "🎖️"
        }

        # Формирование данных для шаблона
        for date_str, instances in grouped_by_date.items():
            date_data = {
                "date": date_str,
                "instances": []
            }
            
            for instance, reports in instances.items():
                instance_data = {
                    "name": instance,
                    "icon": instance_icons.get(instance, ""),
                    "reports": [report['Название'] for report in reports]
                }
                date_data["instances"].append(instance_data)
            
            template_data["dates"].append(date_data)

        # Загружаем шаблон и формируем текст уведомления
        response_text = await load_template_text(
            template_name="upcoming_reports",
            **template_data
        )
    
    else:
        response_text = await load_template_text(
            "not_awailable_reports"
        )
    
    return response_text