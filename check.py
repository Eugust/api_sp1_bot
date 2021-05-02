import os

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)
headers = {
        "Authorization": f"OAuth{PRAKTIKUM_TOKEN}"
}
data = {
        "from_date": 0
}
text = requests.get("https://praktikum.yandex.ru/api/user_api/homework_statuses/", params=data, headers=headers).json()
# text = headers.get('Authorization')
bot.send_message(CHAT_ID, text)