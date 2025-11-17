from datetime import datetime
from typing import Any, Dict

from dadata import DadataAsync

from config import DADATA_KEY
from schemas.user import UserResponse

def timestamp_to_date(timestamp_ms, format_str='%d.%m.%Y'):
    """Convert timestamp in milliseconds to formatted date string"""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime(format_str)


def prepare_company_data_for_template(api_response):
    """
    Преобразует ответ API в структуру данных, подходящую для шаблона.
    """

    company_data = {
        "name_short": ((api_response.get("data") or {}).get("name") or {}).get("short_with_opf", ""),
        "name_full": ((api_response.get("data") or {}).get("name") or {}).get("full_with_opf", ""),
        "status": "Действующая" if ((api_response.get("data") or {}).get("state") or {}).get("status") == "ACTIVE" else "Не действующая",
        "requisites": {
            "INN": (api_response.get("data") or {}).get("inn", ""),
            "KPP": (api_response.get("data") or {}).get("kpp", ""),
            "OGRN": (api_response.get("data") or {}).get("ogrn", ""),
            "OKPO": (api_response.get("data") or {}).get("okpo", ""),
            "OKTMO": (api_response.get("data") or {}).get("oktmo", ""),
            "OKVED": (api_response.get("data") or {}).get("okved", ""),
        },
        "address": {
            "full_address": ((api_response.get("data") or {}).get("address") or {}).get("unrestricted_value", ""),
            "postal_code": (((api_response.get("data") or {}).get("address") or {}).get("data") or {}).get("postal_code", ""),
            "federal_district": (((api_response.get("data") or {}).get("address") or {}).get("data") or {}).get("federal_district", ""),
            "region": (((api_response.get("data") or {}).get("address") or {}).get("data") or {}).get("region_with_type", ""),
            "city": (((api_response.get("data") or {}).get("address") or {}).get("data") or {}).get("city_with_type", ""),
        },
        "financial": {
            "capital": (((api_response.get("data") or {}).get("capital")) or {}).get("value", 0),
            "tax_system": (((api_response.get("data") or {}).get("finance")) or {}).get("tax_system", ""),
            "year": (((api_response.get("data") or {}).get("finance")) or {}).get("year", ""),
        },
        "management": [],
        "founders": [],
        "activities": [],
        "contacts": [],
        "dates": {
            "registration_date": timestamp_to_date((((api_response.get("data") or {}).get("state")) or {}).get("registration_date")),
            "update_date": timestamp_to_date((((api_response.get("data") or {}).get("state")) or {}).get("actuality_date")),
            "current_year": datetime.now().year,
        }
    }

    # Руководство
    management_info = ((api_response.get("data") or {}).get("management")) or {}
    if management_info:
        company_data["management"].append({
            "name": management_info.get("name", ""),
            "position": management_info.get("post", ""),
            "start_date": timestamp_to_date(management_info.get("start_date"))
        })

    # Учредители
    founders_list = (api_response.get("data") or {}).get("founders") or []
    for founder in founders_list:
        if not founder:
            continue
        founder_name = ""
        fio = founder.get("fio", {})
        if fio:
            founder_name = f"{fio.get('surname', '')} {fio.get('name', '')} {fio.get('patronymic', '')}".strip()
        else:
            # Если fio нет, но есть source, используем его
            founder_name = founder.get("fio", {}).get("source", "") or founder.get("name", "")

        company_data["founders"].append({
            "name": founder_name,
            "INN": founder.get("inn", ""),
            "share": (founder.get("share") or {}).get("value", 0)
        })

    # Виды деятельности
    okveds_list = (api_response.get("data") or {}).get("okveds") or []
    for activity in okveds_list:
        if not activity:
            continue
        company_data["activities"].append({
            "code": activity.get("code", ""),
            "name": activity.get("name", ""),
            "type": "Основной" if activity.get("main") else "Дополнительный"
        })

    # Контакты (Emails)
    emails_list = (api_response.get("data") or {}).get("emails") or []
    for email in emails_list:
        if not email:
            continue
        company_data["contacts"].append({
            "type": "Email",
            "value": email.get("value", "")
        })

    phones_list = (api_response.get("data") or {}).get("phones") or []
    for phone in phones_list:
        if not phone: # Пропускаем пустые элементы
            continue
        company_data["contacts"].append({
            "type": "Телефон",
            "value": phone.get("value", "")
        })


    return {"company": company_data}


async def get_company_info(user: UserResponse) -> Dict[str, Any]:
    """
    Общая логика получения информации о компании по ИНН пользователя.

    :param user: Объект пользователя, содержащий ИНН.
    :return: Словарь с данными для шаблона или {'error': ...} в случае ошибки.
    """
    dadata = DadataAsync(DADATA_KEY)

    if user.inn is None or user.inn == "":
        return {"error": "Необходимо заполнить ИНН организации", "requires_inn": True}

    result = await dadata.find_by_id("party", user.inn)

    # Предполагаем, что result[0] всегда существует и содержит нужные поля
    registration_date = timestamp_to_date(result[0]['data']['state']['registration_date'])

    template_data = {
        'suggestions': result,
        'registration_date': registration_date
    }

    return template_data
