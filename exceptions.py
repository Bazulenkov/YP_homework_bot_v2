"""Own exceptions."""


class HomeworkStatusException(Exception):
    """Неверный статус домашней работы."""


class ResponseCheckError(Exception):
    """Получен ответ от API c неожидаемым форматом данных."""


class EndpointResponseError(Exception):
    """Ошибка ответа API."""

    def __init__(self, *args):
        self.response = args[0] if args else None

    def __str__(self):
        message = (
            "Ошибка при обращении к API Яндекс.Практикума: ",
            f'Код ответа: {self.response.get("code")}',
            f'Сообщение сервера: {self.response.get("message")}',
        )
        return message
