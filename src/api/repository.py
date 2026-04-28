from typing import Any
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from src.core.database import async_engine, AsyncSessionLocal
from src.models.models import Base, NotesOrm, NotificationStatus
from src.schemas.schemas import TaskCreate, TaskSchema


class TaskRepository:
    @classmethod
    async def create_tables(cls) -> None:
        """Асинхронно создаёт все таблицы в базе данных."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def delete_tables(cls) -> None:
        """Асинхронно удаляет все таблицы из базы данных."""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @classmethod
    async def create_note(cls, data: TaskCreate) -> TaskSchema:
        """Асинхронно создаёт новую заметку в базе данных."""
        async with AsyncSessionLocal() as session:
            task_dict = data.model_dump()
            if data.remind_after_minutes is not None:
                reminder_time = datetime.now(timezone.utc) + timedelta(
                    minutes=data.remind_after_minutes
                )
                task_dict['reminder_at'] = reminder_time
            new_note = NotesOrm(**task_dict)
            session.add(new_note)
            await session.commit()
            await session.refresh(new_note)
            return TaskSchema.model_validate(new_note)

    @classmethod
    async def update_note(
        cls,
        note_id: int,
        **kwargs: Any
    ) -> TaskSchema | None:
        """Асинхронно обновляет существующую заметку по её id."""
        async with AsyncSessionLocal() as session:
            note = await session.get(NotesOrm, note_id)
            if not note:
                return None
            if 'name' in kwargs:
                note.name = kwargs['name']
            if 'description' in kwargs:
                note.description = kwargs['description']
            if 'remind_after_minutes' in kwargs:
                remind = kwargs['remind_after_minutes']
                note.remind_after_minutes = remind
                note.reminder_at = (
                    datetime.now(timezone.utc) + timedelta(minutes=remind)
                    if remind
                    else None
                )
                note.status = (
                    NotificationStatus.IN_PROGRESS
                    if remind
                    else NotificationStatus.NO_TIMER
                )
                note.time_stamp = datetime.now(timezone.utc)

            session.add(note)
            await session.commit()
            await session.refresh(note)
            return TaskSchema.model_validate(note)

    @classmethod
    async def show_notes(cls) -> list[TaskSchema]:
        """Возвращает список всех заметок из базы данных."""
        async with AsyncSessionLocal() as session:
            query = select(NotesOrm)
            result = await session.execute(query)
            note_models = result.scalars().all()
            return [TaskSchema.model_validate(note) for note in note_models]

    @classmethod
    async def delete_note(cls, note_id: int) -> None:
        """Асинхронно удаляет заметку по её id."""
        async with AsyncSessionLocal() as session:
            note = await session.get(NotesOrm, note_id)
            if not note:
                raise ValueError(f"Заметка с id={note_id} не найдена")
            await session.delete(note)
            await session.commit()