from fastapi import FastAPI, Depends
from schemas import TaskCreate
from repository import TaskRepository
from router import router


def lifespan(app: FastAPI):
    TaskRepository.delete_tables()
    print('Таблицы удалены')
    TaskRepository.create_tables()
    print('Таблицы созданы')
    for n in range(1, 6):
        task_data = TaskCreate(
            name=f'ЗАМЕТКА # {n}',
            description=f'ПРОВЕРКА # {n}',
            remind_after_minutes=None
        )
        TaskRepository.create_note(task_data)
    TaskRepository.create_note(
        TaskCreate(
            name='ПРОВЕРКА СОЗДАНИЯ ЗАМЕТКИ С ТАЙМЕРОМ',
            description='ПРОВЕРКА',
            remind_after_minutes=30
         )
        )
    TaskRepository.update_note(
        note_id=1,
        name='Проверка редактирования заметки',
        description='ПРОВЕРКА',
        remind_after_minutes=None
    )
    yield
    print('Выключение')


app = FastAPI(lifespan=lifespan)
app.include_router(router)
