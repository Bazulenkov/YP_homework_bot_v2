"""Телеграм-бот, который присылает уведомления о статусе домашней работы."""

import logging
import os
import time
from typing import Dict

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PRACTICUM_TOKEN = os.getenv("practikum_token")
TELEGRAM_TOKEN = os.getenv("telegram_token")
TELEGRAM_CHAT_ID = os.getenv("telegram_chat")

RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}

HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}


def send_message(bot: telegram.Bot, message: str):
    """Отправляет сообщение в Telegram чат.

    Чат определяется переменной окружения TELEGRAM_CHAT_ID.
    Args:
        bot: объект бота телеграм.
        message: строка с текстом сообщения к отправке.

    Returns:
        Результат отправки сообщения.
    """
    return bot.send_message(chat_id=TELEGRAM_CHAT_ID, message=message)


def get_api_answer(current_timestamp: int = None) -> Dict:
    """Делает запрос к эндпоинту API-сервиса.

    Args:
        current_timestamp: временная метка в формате Unix time.

    Returns:
        В случае успешного запроса возвращает ответ API, преобразовав его
    из формата JSON к типам данных Python.
        Либо словарь со списком ошибок.
    """
    url = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
    headers = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
    timestamp = current_timestamp or int(time.time())
    params = {"from_date": timestamp}

    try:
        response = requests.get(url, params, headers=headers)
    except Exception as error:
        logger.error(error)
        return {"errors": error}
    else:
        return response.json()


def check_response(response):
    """Проверяет ответ API на корректность.

    Args:
        response: ответ API, приведенный к типам данных Python.

    Returns:
        Если ответ API соответствует ожиданиям, то функция вернет
    список домашних работ (он может быть и пустым),
    доступный в ответе API по ключу 'homeworks'.
    """
    ...


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы.

    Args:
        homework - один элемент из списка домашних работ.

    Returns:
        В случае успеха, функция возвращает подготовленную для отправки в
        Telegram строку, содержащую один из вердиктов
        словаря HOMEWORK_STATUSES.
    """
    homework_name = ...
    homework_status = ...

    ...

    verdict = ...

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения.

    Returns:
        Если отсутствует хотя бы одна переменная окружения — вернет False,
     иначе — True.
    """
    if (
        PRACTICUM_TOKEN is None
        or TELEGRAM_CHAT_ID is None
        or TELEGRAM_TOKEN is None
    ):
        return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        ...

    get_api_answer()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f" Сбой в работе программы: {error}"
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == "__main__":
    main()
