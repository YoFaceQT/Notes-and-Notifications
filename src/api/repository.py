from datetime import datetime, timedelta

from sqlalchemy import select

from database import sync_engine, session_base
from src.models.models import Base, NotesOrm, NotificationStatus
from src.schemas.schemas import TaskCreate, TaskSchema


class TaskRepository:
    @classmethod
    def create_tables(cls):
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)

    @classmethod
    def delete_tables(cls):
        sync_engine.echo = False
        Base.metadata.drop_all(sync_engine)

    @classmethod
    def create_note(cls, data: TaskCreate) -> int:
        """Создаёт новую заметку с возможностью установки напоминания."""
        with session_base() as session:
            task_dict = data.model_dump()
            if data.remind_after_minutes is not None:
                reminder_time = datetime.now() + timedelta(
                    minutes=data.remind_after_minutes
                )
                task_dict['reminder_at'] = reminder_time
            new_note = NotesOrm(**task_dict)
            session.add(new_note)
            session.commit()
            return new_note.id

    @classmethod
    def get_note(cls, note_id):
        with session_base() as session:
            note = session.get(NotesOrm, note_id)
            if not note:
                raise ValueError(f"Заметка с id={note_id} не найдена")
            return note

    @classmethod
    def update_note(
        cls,
        note_id,
        name=None,
        description=None,
        remind_after_minutes=None
    ):
        with session_base() as session:
            note = session.get(NotesOrm, note_id)
            if not note:
                raise ValueError(f"Заметка с id={note_id} не найдена")
            if name is not None:
                note.name = name
            if description is not None:
                note.description = description
            if remind_after_minutes is not None:
                note.remind_after_minutes = remind_after_minutes
                note.status = NotificationStatus.IN_PROGRESS
            else:
                note.remind_after_minutes = None
                note.status = NotificationStatus.NO_TIMER
            session.add(note)
            session.commit()
            return note

    @classmethod
    def show_notes(cls) -> list[TaskSchema]:
        with session_base() as session:
            query = select(NotesOrm)
            result = session.execute(query)
            note_models = result.scalars().all()
            notes_schemas = [TaskSchema.model_validate(note_model)
                             for note_model in note_models]
            return notes_schemas

    @classmethod
    def delete_note(cls, note_id):
        with session_base() as session:
            note = session.get(NotesOrm, note_id)
            if not note:
                raise ValueError(f"Заметка с id={note_id} не найдена")
            session.delete(note)
            session.commit()
            return note_id
