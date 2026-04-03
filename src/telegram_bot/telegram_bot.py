import asyncio
from datetime import datetime
import logging
import os

from dotenv import load_dotenv
import requests
import telebot
from telebot import TeleBot
import threading

from database import session_base
from src.models.models import NotesOrm, NotificationStatus


load_dotenv()

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


logging.getLogger("urllib3").setLevel(logging.WARNING)

handler = logging.StreamHandler()

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - '
    '[%(funcName)s:%(lineno)d] - '
    '%(message)s'
)
handler.setFormatter(formatter)

file_handler = logging.FileHandler('main.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def check_tokens():
    """Проверяет доступность обязательных переменных окружения."""
    required_tokens = ('TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')

    missing_tokens = []

    for token_name in required_tokens:
        token_value = globals().get(token_name)
        if not token_value:
            missing_tokens.append(token_name)

    if missing_tokens:
        error_message = (
            f'Отсутствуют переменные окружения: {', '.join(missing_tokens)}. '
            'Программа не может быть запущена.'
        )
        logging.critical(error_message)
        raise EnvironmentError(error_message)

    logging.info('Все необходимые переменные окружения Telegram бота доступны')


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    logging.debug('Начало отправки сообщения в Telegram')

    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение успешно отправлено в Telegram')
    except (telebot.apihelper.ApiException,
            requests.RequestException) as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')


def check_and_notify(bot):
    """Проверяет, не наступило ли время уведомления для активных заметок
    (IN_PROGRESS).
    """
    with session_base() as session:
        now = datetime.now()
        notes_to_notify = session.query(NotesOrm).filter(
            NotesOrm.reminder_at <= now,
            NotesOrm.status == NotificationStatus.IN_PROGRESS
        ).all()

        for note in notes_to_notify:
            message = (f"[УВЕДОМЛЕНИЕ] Пора заняться заметкой:{note.name} "
                       f"Описание: {note.description}")
            send_message(bot, message)

            note.status = NotificationStatus.NO_TIMER
            session.add(note)
        session.commit()


async def start_scheduler(bot, interval_seconds=30):
    """Асинхронный цикл периодической проверки базы."""
    while True:
        await asyncio.to_thread(check_and_notify, bot)
        await asyncio.sleep(interval_seconds)


def run_bot_polling(bot):
    """Запускает синхронный поллинг бота в отдельном потоке."""
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Ошибка в polling бота: {e}")


async def bot_load():
    """Основная логика: запуск бота и фоновой проверки базы."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)

    try:
        send_message(bot, 'Бот запущен и начал отслеживание таймеров заметок.')
    except Exception as error:
        logging.error(f'Не удалось отправить стартовое сообщение: {error}')

    polling_thread = threading.Thread(
        target=run_bot_polling,
        args=(bot,),
        daemon=True
    )
    polling_thread.start()

    try:
        asyncio.create_task(start_scheduler(bot))
    except Exception as e:
        logging.error(f"Критическая ошибка в логике бота: {e}")
