import os
import time

import requests
import telegram
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='bot.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    filemode='a'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('bot.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_PRAKTIKUM = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
SUCCESS = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'


def parse_homework_status(homework):
    dict_verdict = {
        "rejected": 'К сожалению в работе нашлись ошибки.',
        "reviewing": 'Работа взята в ревью.',
        "approved": SUCCESS
    }
    try:
        homework_name = homework["homework_name"]
        homework_status = homework["status"]
        verdict = dict_verdict[homework_status]
        if homework_status == "reviewing":
            return verdict
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except KeyError as e:
        logging.error(f'Ошибка {e}')
        return "Неверный ответ сервера"


def get_homework_statuses(current_timestamp=None):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {"from_date": current_timestamp}
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    try:
        homework_statuses = requests.get(
            API_PRAKTIKUM,
            params=params,
            headers=headers
        )
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
        logging.error(e)


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    logging.debug("Bot started")
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]
                    ),
                    bot_client
                )
                logging.info("Message sent")
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
