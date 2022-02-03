"""Хандлер логгера для отправки логов в телеграм."""
import logging

import telegram

logger = logging.getLogger(__name__)


class TelegramBotHandler(logging.Handler):
    """Хандлер логгера для отправки логов в телеграм."""

    def __init__(self, token: str, chat_id: str):
        super().__init__()
        self.bot = telegram.Bot(token)
        self.chat_id = chat_id

    def emit(self, record: logging.LogRecord):
        """Отправляет сообщение в Telegram чат.

        Args:
            token: токен бота телеграм.
            chat_id: ID чата, в который бот должен отправить сообщение;

        Raises:
            :class:`telegram.error.TelegramError`
        """
        try:
            msg = self.format(record)
            posted_message = self.bot.send_message(
                chat_id=self.chat_id, text=msg
            )
            logger.info(f'Сообщение отправлено в Telegram: "{msg}"')
            return posted_message
        except telegram.error.TelegramError as e:
            logger.error(e)
            raise e
