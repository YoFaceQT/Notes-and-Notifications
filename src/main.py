from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.repository import TaskRepository
from src.api.router import router
from src.telegram_bot.async_telegram_bot import bot_load


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await TaskRepository.delete_tables()
    await TaskRepository.create_tables()

    bot_task = asyncio.create_task(bot_load())
    yield
    bot_task.cancel()
    await asyncio.gather(bot_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
