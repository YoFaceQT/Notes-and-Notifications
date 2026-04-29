import asyncio
import logging
import sys
import json
from aiogram import Bot, Dispatcher
from src.core.config import settings
from faststream.rabbit import RabbitBroker
from src.core.database import AsyncSessionLocal
from sqlalchemy import select
from faststream.rabbit import RabbitBroker
from src.models.models import NotesOrm, NotificationStatus
from src.core.config import settings


RABBIT_URL =(
    f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@"
    f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
)


dp = Dispatcher()

bot = Bot(token=settings.TELEGRAM_TOKEN)

broker = RabbitBroker(RABBIT_URL)

@broker.subscriber("messages")
async def handle_messages_and_send_message(data: str):
    try:
        payload = json.loads(data)
        note_id = payload["note_id"]
        message_text = payload["message"]

        await bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=message_text,
        )


        async with AsyncSessionLocal() as session:
            stmt = select(NotesOrm).where(NotesOrm.id == note_id)
            result = await session.execute(stmt)
            note = result.scalar_one_or_none()
            if note:
                note.status = NotificationStatus.SUCCESSFULLY_SENT
                session.add(note)
                await session.commit()
                logging.info(
                    f"Статус заметки {note_id} обновлён на SUCCESSFULLY_SENT"
                )
            else:
                logging.warning(f"Заметка {note_id} не найдена")

    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")

async def main() -> None:
    async with broker:
        await broker.start()
        logging.info("Брокер стартовал")
        await dp.start_polling(bot)
    logging.info("Брокер завершил работу")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())