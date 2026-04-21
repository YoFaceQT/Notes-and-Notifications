import asyncio
from datetime import datetime, timezone
import logging
import os

from dotenv import load_dotenv
import requests
import telebot
from telebot import TeleBot
import threading

from core.database import session_base
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


def check_tokens() -> None:
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


def send_message(bot: TeleBot, message: str) -> bool:
    """Отправляет сообщение в Telegram-чат."""
    logging.debug('Начало отправки сообщения в Telegram')

    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение успешно отправлено в Telegram')
        return True
    except (telebot.apihelper.ApiException,
            requests.RequestException) as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')
        return False


def check_and_notify(bot: TeleBot) -> None:
    """Проверяет, не наступило ли время уведомления для активных заметок
    (IN_PROGRESS).
    """
    with session_base() as session:
        now = datetime.now(timezone.utc)
        notes_to_notify = session.query(NotesOrm).filter(
            NotesOrm.reminder_at <= now,
            NotesOrm.status == NotificationStatus.IN_PROGRESS
        ).all()

        for note in notes_to_notify:
            if not note.description:
                message = (f"[УВЕДОМЛЕНИЕ] Пора заняться заметкой:{note.name}")
            else:
                message = (f"[УВЕДОМЛЕНИЕ] Пора заняться заметкой:{note.name} "
                           f"Описание: {note.description}")
            if send_message(bot, message):
                note.status = NotificationStatus.SUCCESSFULLY_SENT
                note.reminder_at = None
                note.remind_after_minutes = None
                session.add(note)
            else:
                note.status = NotificationStatus.FAILED_TO_SEND
                session.add(note)
        session.commit()


async def start_scheduler(bot: TeleBot, interval_seconds: int = 30) -> None:
    """Асинхронный цикл периодической проверки базы."""
    while True:
        await asyncio.to_thread(check_and_notify, bot)
        await asyncio.sleep(interval_seconds)


def run_bot_polling(bot: TeleBot) -> None:
    """Запускает синхронный поллинг бота в отдельном потоке."""
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Ошибка в polling бота: {e}")


async def bot_load() -> None:
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
