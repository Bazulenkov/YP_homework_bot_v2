[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус домашней работы: взята ли домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

## Функционал бота:

- Периодически опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;  
    > Период задается константой `RETRY_TIME`
- При обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram;
- Логирует свою работу.
- При возникновении ошибок уровня ERROR сообщает в Telegram.

В ветке ` update.TelegramHandler ` реализована отправка ошибок в Telegram при помощи написанного хендлера для логгера.

## Built With
- [Python](https://www.python.org/)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

## Authors
* **Anton Bazulenkov** - *Initial work* - [Bazulenkov](https://github.com/Bazulenkov)

