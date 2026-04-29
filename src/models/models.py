from datetime import datetime, timezone
import enum

from sqlalchemy import DateTime, Enum, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


metadata_obj = MetaData()


class Base(DeclarativeBase):
    pass


class NotificationStatus(enum.Enum):
    NO_TIMER = 'NO_TIMER'
    IN_PROGRESS = 'IN_PROGRESS'
    FAILED_TO_SEND = 'FAILED_TO_SEND'
    SUCCESSFULLY_SENT = 'SUCCESSFULLY_SENT'
    PROCESSING = 'PROCESSING'


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class NotesOrm(Base):
    """Модель Заметки"""
    __tablename__ = 'notes'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(nullable=True)
    remind_after_minutes: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus),
        default=NotificationStatus.NO_TIMER,
        nullable=False
    )
    time_stamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now
    )
    reminder_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
        )

    def __str__(self) -> str:
        return (
            f"NotesOrm(id={self.id}, "
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"time_stamp={self.time_stamp}, "
            f"remind_after_minutes={self.remind_after_minutes}, "
            f"status={self.status})"
        )
