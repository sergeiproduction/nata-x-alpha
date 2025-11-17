import os
from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("Не найдена переменная окружения BOT_TOKEN в файле .env")


USER_AGREEMENT = os.getenv("USER_AGREEMENT")
PRIVACY_POLICY = os.getenv("PRIVACY_POLICY")

DATABASE_URL = os.getenv("DATABASE_URL")
MISTRAL_TOKEN = os.getenv("MISTRAL_KEY")
DADATA_KEY = os.getenv("DADATA_KEY")