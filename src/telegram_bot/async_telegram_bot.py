import asyncio
from datetime import datetime, timezone
import logging
import os
import json
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from sqlalchemy import select

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.models.models import NotesOrm, NotificationStatus
from src.broker.broker import broker

load_dotenv()

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(level=logging.INFO)


bot = Bot(token=settings.TELEGRAM_TOKEN)

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


async def send_message_via_broker(note_id: int, message: str) -> bool:
    """Публикует JSON с id заметки и текстом в очередь 'messages'."""
    try:
        payload = json.dumps({
            "note_id": note_id,
            "message": message
        })
        await broker.publish(payload, queue="messages")
        logging.debug(f"Опубликовано для заметки {note_id}: {message[:50]}...")
        return True
    except Exception as e:
        logging.error(f"Ошибка публикации в брокер: {e}")
        return False


async def check_and_notify(bot: Bot) -> None:
    async with AsyncSessionLocal() as session:
        now = datetime.now(timezone.utc)
        stmt = select(NotesOrm).where(
            NotesOrm.reminder_at <= now,
            NotesOrm.status == NotificationStatus.IN_PROGRESS
        )
        result = await session.execute(stmt)
        notes_to_notify = result.scalars().all()

        for note in notes_to_notify:
            message = f"Пора заняться заметкой: {note.name}"
            if note.description:
                message += f"\nОписание: {note.description}"

            if await send_message_via_broker(note.id, message):

                note.status = NotificationStatus.PROCESSING
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


async def bot_load() -> None:
    """Основная логика: запуск бота и фоновой проверки базы."""
    check_tokens()
    bot = Bot(token=settings.TELEGRAM_TOKEN)

    try:
        await bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID ,
            text='Бот запущен и начал отслеживание таймеров заметок.'
        )
    except Exception as error:
        logging.error(f'Не удалось отправить стартовое сообщение: {error}')

    scheduler_task = asyncio.create_task(start_scheduler(bot))
    polling_task = asyncio.create_task(dp.start_polling(bot))

    await asyncio.gather(scheduler_task, polling_task)
