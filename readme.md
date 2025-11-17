# NataXAlpha: Инструкция по запуску

Вы также можете сразу перейти в чат-бот [NataXAlpha](t.me/nataxalpha_bot "Чат-бот в Telegram")

## Предварительные требования
- Python 3.8+
- PostgreSQL 12+
- SQLite3.24+
- Установленные системные шрифты

## Шаги по запуску

### 1. Настройка конфигурации
В файле `config.py` укажите необходимые токены и ссылки:

```python
BOT_TOKEN = "your_telegram_bot_token_here"
MISTRAL_KEY = "your_mistral_api_key_here"
```

### 2\. Установка Alembic
 
Установите Alembic для управления миграциями базы данных:
 
bash
 

    pip install alembic

### 3\. Генерация миграций
 
Создайте и примените миграции базы данных:
 
bash
 

    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head

### 4\. Установка шрифтов
 
Для корректного отображения текста при генерации промокодов установите шрифты из папки `fonts/`:
 
**Windows:**
 

*   Скопируйте файлы из `fonts/` в `C:\Windows\Fonts\`
     
*   Или выполните установку через двойной клик по каждому файлу .ttf
     

**Linux:**
 
bash
 

    sudo cp fonts/* /usr/share/fonts/truetype/
    sudo fc-cache -f -v

**macOS:**
 

*   Откройте каждый файл .ttf и нажмите "Установить шрифт"
     
*   Или скопируйте в `/Library/Fonts/`
     

### 5\. Запуск приложения
 
Запустите основное приложение:
 
bash
 

    python app.py

## Проверка работоспособности
 
После запуска проверьте:
 

*   Бот отвечает в Telegram
     
*   База данных подключена корректно
     
*   Генерация промокодов работает с правильными шрифтами
     
*   LLM-модель отвечает на запросы