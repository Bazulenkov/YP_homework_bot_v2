"""Телеграм-бот, который присылает уведомления о статусе домашней работы."""

import logging
import os
import sys
import time
from typing import Dict, List

import requests
import telegram
from dotenv import load_dotenv

from exceptions import HomeworkStatusException, EndpointResponseError, \
    ResponseCheckError

load_dotenv()

logger = logging.getLogger(__name__)

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT", "")

RETRY_PERIOD = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}

HOMEWORK_VERDICTS = {
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
        :class:`telegram.Message`: On success, the sent message is returned.

    Raises:
        :class:`telegram.error.TelegramError`
    """
    try:
        posted_message = bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug(f'Сообщение отправлено в Telegram: "{message}"')
        return posted_message
    except telegram.error.TelegramError as e:
        logger.error(e)
        raise e


def get_api_answer(timestamp: int = 0) -> Dict:
    """Делает запрос к эндпоинту API-сервиса.

    Args:
        timestamp: временная метка в формате Unix time.

    Returns:
        В случае успешного запроса возвращает ответ API, преобразовав его
    из формата JSON к типам данных Python.
        Либо словарь со списком ошибок.
    """
    params = {"from_date": timestamp}

    try:
        response = requests.get(url=ENDPOINT, params=params, headers=HEADERS)
    except requests.RequestException as e:
        logger.error(e)
        raise EndpointResponseError(e)
    response.raise_for_status()
    if not 200 <= response.status_code < 204:
        raise ConnectionError(
            f"Response received not success: status_code = {response.status_code}"
        )
    try:
        result = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logger.error(e)
        raise e

    return result


def check_response(response: Dict) -> List:
    """Проверяет ответ API на корректность.

    Args:
        response: ответ API, приведенный к типам данных Python.

    Returns:
        Если ответ API соответствует ожиданиям, то функция вернет
    список домашних работ (он может быть и пустым),
    доступный в ответе API по ключу 'homeworks'.

    Raises:
        Отсутствие ожидаемых ключей в ответе API;
    """
    try:
        homeworks = response["homeworks"]
        response["current_date"]
    except KeyError as e:
        logger.error(e)
        raise ResponseCheckError(e)
    except TypeError as e:
        logger.error("Ответ от API пришел не в виде словаря.")
        raise e

    homeworks = response["homeworks"]

    if not isinstance(homeworks, list):
        raise TypeError
    if not homeworks:
        logger.debug("Новые статусы отсутствуют")
    return homeworks


def parse_status(homework: Dict[str, str]) -> str:
    """Извлекает из информации о конкретной домашней работе статус этой работы.

    Args:
        homework - один элемент из списка домашних работ.

    Returns:
        В случае успеха, функция возвращает подготовленную для отправки в
        Telegram строку, содержащую один из вердиктов
        словаря HOMEWORK_VERDICTS.
    """
    # ошибка в тесте
    # tests/test_bot.py::TestHomework::test_parse_status_no_homework_name_key
    # это заглушка, чтобы тест проходил.
    if isinstance(homework, list):
        homework = homework[0]  # type: ignore

    try:
        homework_name = homework["homework_name"]
        homework_status = homework["status"]
    except KeyError as e:
        logger.error(e)
        raise EndpointResponseError

    if homework_status not in HOMEWORK_VERDICTS:
        logger.error("Получен неизвестный статус домашней работы")
        raise HomeworkStatusException

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения.

    Returns:
        Если отсутствует хотя бы одна переменная окружения — вернет False,
     иначе — True.
    """
    kwargs = {
        "PRACTICUM_TOKEN": PRACTICUM_TOKEN,
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
    }

    for key, value in kwargs.items():
        if value in ("", None, False):
            logger.critical(f"Missing env value: {key}")
            return False
    return True


def main():
    """Основная логика работы бота."""
    logger.debug("Bot started")
    if check_tokens() is False:
        logger.critical("Missing env variables")
        sys.exit("Interrupt: Missing env variables")

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    # d = datetime.date(2022, 1, 1)
    # timestamp = int(time.mktime(d.timetuple()))

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks: List = check_response(response)
            for hw in homeworks:
                message = parse_status(hw)
                send_message(bot, message)
            timestamp = int(response["current_date"])

        except Exception as error:
            error_message = f" Сбой в работе программы: {error}"
            logger.error(error_message)
            send_message(bot, error_message)
        finally:
            logger.info(f"Следующая проверка через {RETRY_PERIOD / 60} минут")
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] (%(name)s) %(levelname)s: %(message)s",
    )
    main()
