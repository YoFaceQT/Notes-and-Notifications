import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from datetime import datetime, timezone
from sqlalchemy import select
from src.models.models import NotesOrm, NotificationStatus
from src.core.database import AsyncSessionLocal


load_dotenv()

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(level=logging.INFO)


bot = Bot(token=TELEGRAM_TOKEN)

dp = Dispatcher()

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



async def send_message_aiogram(
        bot: Bot,
        TELEGRAM_CHAT_ID: int,
        message: str
    ) -> bool:
    """Отправляет сообщение в Telegram-чат."""
    logging.debug('Начало отправки сообщения в Telegram')
    try:
        await bot.send_message(TELEGRAM_CHAT_ID, message)
        return True
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')
        return False
    


async def check_and_notify(bot: Bot) -> None:
    """Проверяет, не наступило ли время уведомления для активных заметок
    (IN_PROGRESS).
    """
    async with AsyncSessionLocal() as session: 
        now = datetime.now(timezone.utc)
        notes_to_notify = select(NotesOrm).where(
            NotesOrm.reminder_at <= now,
            NotesOrm.status == NotificationStatus.IN_PROGRESS
        )

        result = await session.execute(notes_to_notify)        
        notes_to_notify = result.scalars().all()


        for note in notes_to_notify:
            if not note.description:
                message = (f"[УВЕДОМЛЕНИЕ] Пора заняться заметкой:{note.name}")
            else:
                message = (f"[УВЕДОМЛЕНИЕ] Пора заняться заметкой:{note.name} "
                           f"Описание: {note.description}")
            if await send_message_aiogram(bot, TELEGRAM_CHAT_ID, message):
                note.status = NotificationStatus.SUCCESSFULLY_SENT
                note.reminder_at = None
                note.remind_after_minutes = None
                session.add(note)
            else:
                note.status = NotificationStatus.FAILED_TO_SEND
                session.add(note)
        await session.commit()


async def start_scheduler(bot: Bot, interval_seconds: int = 30) -> None:
    """Асинхронный цикл периодической проверки базы."""
    while True:
        await check_and_notify(bot)
        await asyncio.sleep(interval_seconds)


async def run_bot_polling(bot: Bot) -> None:
    """Запускает асинхронный поллинг бота в отдельном потоке."""
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка в polling бота: {e}")


async def bot_load() -> None:
    """Основная логика: запуск бота и фоновой проверки базы."""
    check_tokens()
    bot = Bot(token=TELEGRAM_TOKEN)


    try:
        await send_message_aiogram(
            bot,
            TELEGRAM_CHAT_ID,
            'Бот запущен и начал отслеживание таймеров заметок.'
        )
    except Exception as error:
        logging.error(f'Не удалось отправить стартовое сообщение: {error}')


    scheduler_task = asyncio.create_task(start_scheduler(bot))
    polling_task = asyncio.create_task(dp.start_polling(bot))


    await asyncio.gather(scheduler_task, polling_task)

