from collections.abc import AsyncIterator

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.repository import TaskRepository
from src.api.router import router
from src.telegram_bot.telegram_bot import bot_load

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    TaskRepository.delete_tables()

    TaskRepository.create_tables()

    await bot_load()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
