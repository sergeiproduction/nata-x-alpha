import asyncio
from datetime import datetime, timedelta
from typing import List, Dict

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from bot.services.user import UserService
from reports.calendar import ReportCalendar
from bot.services.notification_type import NotificationTypeService
from bot.services.user_notification import UserNotificationService
from utils.templates import load_template_text


async def send_upcoming_reports_notifications(
    notification_type_service: NotificationTypeService,
    user_notification_service: UserNotificationService,
    user_service: UserService,
    calendar_file_path: str = "./storage/report_calendar.json",
    templates_dir: str = './templates/',
    bot = None
):
    """
    Фоновое задание для отправки уведомлений о предстоящих отчетах
    """
    
    # Загружаем календарь отчетов
    calendar = ReportCalendar()
    calendar.load_calendar_from_json(calendar_file_path)
    
    # Получаем все типы уведомлений
    general_notification_type = await notification_type_service.get_notification_type_by_name("уведомления")
    advance_notification_type = await notification_type_service.get_notification_type_by_name("за 3 дня")
    
    if not general_notification_type:
        return  # Общая настройка уведомлений не найдена
    
    if not advance_notification_type:
        return  # Тип уведомления "за 3 дня" не найден
    
    # Получаем все отчеты из календаря
    all_reports = calendar.reports
    
    # Определяем сегодняшнюю дату и даты на ближайшие 3 дня
    today = datetime.now().date()
    next_3_days = [today + timedelta(days=i) for i in range(1, 4)]  # следующие 3 дня
    today_date = [today]  # сегодняшняя дата для уведомлений в день отчета
    
    # Находим отчеты, срок сдачи которых приходится на ближайшие 3 дня (для уведомлений за 3 дня)
    upcoming_reports_advance = []
    for report in all_reports:
        report_date_str = report["Дата сдачи"]
        report_date = datetime.strptime(report_date_str, "%d.%m.%Y").date()
        
        if report_date in next_3_days:
            upcoming_reports_advance.append(report)
    
    # Находим отчеты, срок сдачи которых приходится на сегодня (для уведомлений в день отчета)
    today_reports = []
    for report in all_reports:
        report_date_str = report["Дата сдачи"]
        report_date = datetime.strptime(report_date_str, "%d.%m.%Y").date()
        
        if report_date in today_date:
            today_reports.append(report)
    
    # Группируем отчеты по дате и инстанции для уведомлений за 3 дня
    grouped_reports_advance = _group_reports_by_date_and_instance(upcoming_reports_advance)
    
    # Группируем отчеты по дате и инстанции для уведомлений в день отчета
    grouped_reports_today = _group_reports_by_date_and_instance(today_reports)
    
    # Получаем всех пользователей
    all_users = await user_service.list_users()
    
    for user in all_users:
        user_id = user.id
        
        # Проверяем, включена ли общая настройка "уведомления" для пользователя
        general_setting = await user_notification_service.get_user_notification(
            user_id, general_notification_type.id
        )
        if not general_setting or not general_setting.is_active:
            continue  # Общие уведомления отключены для этого пользователя
        
        # Проверяем, включена ли настройка "за 3 дня" для пользователя
        advance_setting = await user_notification_service.get_user_notification(
            user_id, advance_notification_type.id
        )
        
        # Получаем активные настройки инстанций (ФНС, СФР, Военкомат)
        active_instance_names = await user_notification_service.get_active_notification_type_names(user_id)
        
        # Если "за 3 дня" включено, отправляем уведомления за 3 дня
        if advance_setting and advance_setting.is_active:
            await _send_advance_notifications(
                user.telegram_id, grouped_reports_advance, active_instance_names, templates_dir, bot
            )
        # Если "за 3 дня" выключено, отправляем уведомления в день отчета
        else:
            await _send_today_notifications(
                user.telegram_id, grouped_reports_today, active_instance_names, templates_dir, bot
            )


async def send_notification_to_user(user_id: int, date_str: str, instances: Dict[str, List[Dict]], templates_dir: str, bot: Bot):
    """
    Отправка уведомления пользователю о предстоящих отчетах
    """
    # Формируем данные для шаблона
    template_data = {
        "date": date_str,
        "instances": [],
        "is_month_calendar": False  # Это уведомление, а не календарь на месяц
    }
    
    # Добавляем иконки для инстанций
    instance_icons = {
        "ФНС": "🏛️",
        "СФР": "👥",
        "Военкомат": "🏛️"  # или другая иконка по желанию
    }
    
    for instance, reports in instances.items():
        instance_data = {
            "name": instance,
            "icon": instance_icons.get(instance, ""),
            "reports": [report["name"] for report in reports]
        }
        template_data["instances"].append(instance_data)
    
    # Загружаем шаблон и формируем текст уведомления
    notification_text = await load_template_text(
        template_name="upcoming_reports",
        templates_dir=templates_dir,
        **template_data
    )
    
    try:
        await bot.send_message(user_id, notification_text)
    except TelegramBadRequest as e:
        if "chat not found" in str(e):
            # Пользователь не инициировал общение с ботом или заблокировал его
            print(f"Не удалось отправить уведомление пользователю {user_id}: чат не найден")
        else:
            print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при отправке уведомления пользователю {user_id}: {e}")


def _group_reports_by_date_and_instance(reports: List[Dict]) -> Dict[str, Dict[str, List[Dict]]]:
    """
    Группирует отчеты по дате и инстанции
    
    Args:
        reports: Список отчетов
        
    Returns:
        Словарь в формате {date_str: {instance: [{"name": name, "period": period}]}}
    """
    grouped_reports = {}
    for report in reports:
        date_str = report["Дата сдачи"]
        instance = report["Инстанция"]
        
        if date_str not in grouped_reports:
            grouped_reports[date_str] = {}
        
        if instance not in grouped_reports[date_str]:
            grouped_reports[date_str][instance] = []
        
        grouped_reports[date_str][instance].append({
            "name": report["Название"],
            "period": report["Период сдачи"]
        })
    
    return grouped_reports


async def _send_advance_notifications(
    user_id: int, 
    grouped_reports: Dict[str, Dict[str, List[Dict]]], 
    active_instance_names: List[str], 
    templates_dir: str, 
    bot
):
    """
    Отправка уведомлений за 3 дня
    
    Args:
        user_id: ID пользователя
        grouped_reports: Сгруппированные отчеты
        active_instance_names: Активные настройки инстанций
        templates_dir: Директория с шаблонами
        bot: Telegram bot instance
    """
    # Фильтруем сгруппированные отчеты по активным инстанциям пользователя
    filtered_grouped_reports = {}
    for date_str, instances in grouped_reports.items():
        filtered_instances = {}
        for instance, reports in instances.items():
            if instance in active_instance_names:
                filtered_instances[instance] = reports
        
        if filtered_instances:  # Только если есть отчеты по активным инстанциям
            filtered_grouped_reports[date_str] = filtered_instances
    
    # Отправляем уведомления за 3 дня для каждой даты
    for date_str, instances in filtered_grouped_reports.items():
        await send_notification_to_user(user_id, date_str, instances, templates_dir, bot)


async def _send_today_notifications(
    user_id: int, 
    grouped_reports: Dict[str, Dict[str, List[Dict]]], 
    active_instance_names: List[str], 
    templates_dir: str, 
    bot
):
    """
    Отправка уведомлений в день отчета
    
    Args:
        user_id: ID пользователя
        grouped_reports: Сгруппированные отчеты
        active_instance_names: Активные настройки инстанций
        templates_dir: Директория с шаблонами
        bot: Telegram bot instance
    """
    # Фильтруем сгруппированные отчеты по активным инстанциям пользователя
    filtered_grouped_reports = {}
    for date_str, instances in grouped_reports.items():
        filtered_instances = {}
        for instance, reports in instances.items():
            if instance in active_instance_names:
                filtered_instances[instance] = reports
        
        if filtered_instances:  # Только если есть отчеты по активным инстанциям
            filtered_grouped_reports[date_str] = filtered_instances
    
    # Отправляем уведомления в день отчета для каждой даты
    for date_str, instances in filtered_grouped_reports.items():
        await send_notification_to_user(user_id, date_str, instances, templates_dir, bot)


async def start_daily_notification_task(
    notification_type_service: NotificationTypeService,
    user_notification_service: UserNotificationService,
    user_service: UserService,
    calendar_file_path: str = "./storage/report_calendar.json",
    templates_dir: str = './templates/',
    bot = None
):
    """
    Запускает фоновую задачу с периодичностью 1 раз в день
    
    Args:
        notification_type_service: Сервис типов уведомлений
        user_notification_service: Сервис пользовательских уведомлений
        user_service: Сервис пользователей
        calendar_file_path: Путь к файлу календаря
        templates_dir: Директория с шаблонами
        bot: Telegram bot
    """
    while True:
        try:
            await send_upcoming_reports_notifications(
                notification_type_service=notification_type_service,
                user_notification_service=user_notification_service,
                user_service=user_service,
                calendar_file_path=calendar_file_path,
                templates_dir=templates_dir,
                bot=bot
            )
        except Exception as e:
            print(f"Ошибка в фоновом задании уведомлений: {e}")
        
        # Ждем 24 часа перед следующей проверкой
        await asyncio.sleep(24 * 3600)