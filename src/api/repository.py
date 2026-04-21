from typing import Any
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from core.database import sync_engine, session_base
from src.models.models import Base, NotesOrm, NotificationStatus
from src.schemas.schemas import TaskCreate, TaskSchema


class TaskRepository:
    @classmethod
    def create_tables(cls) -> None:
        """Создаёт все таблицы в базе данных."""
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)

    @classmethod
    def delete_tables(cls) -> None:
        """Удаляет все таблицы из базы данных."""
        sync_engine.echo = False
        Base.metadata.drop_all(sync_engine)

    @classmethod
    def create_note(cls, data: TaskCreate) -> TaskSchema:
        """Создаёт новую заметку в базе данных."""
        with session_base() as session:
            task_dict = data.model_dump()
            if data.remind_after_minutes is not None:
                reminder_time = datetime.now(timezone.utc) + timedelta(
                    minutes=data.remind_after_minutes
                )
                task_dict['reminder_at'] = reminder_time
            new_note = NotesOrm(**task_dict)
            session.add(new_note)
            session.commit()
            session.refresh(new_note)
            return TaskSchema.model_validate(new_note)

    @classmethod
    def update_note(cls, note_id: int, **kwargs: Any) -> TaskSchema:
        """ Обновляет существующую заметку по её id."""
        with session_base() as session:
            note = session.get(NotesOrm, note_id)
            if not note:
                raise ValueError(f"Заметка с id={note_id} не найдена")

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
            session.commit()
            session.refresh(note)
            return TaskSchema.model_validate(note)

    @classmethod
    def show_notes(cls) -> list[TaskSchema]:
        """Возвращает список всех заметок из базы данных."""
        with session_base() as session:
            query = select(NotesOrm)
            result = session.execute(query)
            note_models = result.scalars().all()
            return [TaskSchema.model_validate(note) for note in note_models]

    @classmethod
    def delete_note(cls, note_id: int) -> None:
        """Удаляет заметку по её id."""
        with session_base() as session:
            note = session.get(NotesOrm, note_id)
            if not note:
                raise ValueError(f"Заметка с id={note_id} не найдена")
            session.delete(note)
            session.commit()
