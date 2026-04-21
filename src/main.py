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
    print('Таблицы удалены')
    TaskRepository.create_tables()
    print('Таблицы созданы')
    # for n in range(1, 4):
    #     task_data = TaskCreate(
    #         name=f'ЗАМЕТКА # {n}',
    #         description=f'ПРОВЕРКА # {n}',
    #         remind_after_minutes=None
    #     )
    #     TaskRepository.create_note(task_data)
    # TaskRepository.create_note(
    #     TaskCreate(
    #         name='ПРОВЕРКА СОЗДАНИЯ ЗАМЕТКИ С ТАЙМЕРОМ',
    #         remind_after_minutes=1
    #      )
    #     )
    # TaskRepository.update_note(
    #     note_id=1,
    #     name='Проверка редактирования заметки',
    #     description='ПРОВЕРКА',
    #     remind_after_minutes=30
    # )
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
