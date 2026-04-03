from datetime import datetime
import enum

from sqlalchemy import Enum, func, DateTime, MetaData, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


metadata_obj = MetaData()


class Base(DeclarativeBase):
    pass


class NotificationStatus(enum.Enum):
    NO_TIMER = 'no_timer'
    IN_PROGRESS = 'in_progress'
    FAILED_TO_SEND = 'Failed_to_send'


class NotesOrm(Base):
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(nullable=True)
    time_stamp: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', now())")
    )
    remind_after_minutes: Mapped[int | None] = mapped_column(nullable=True)
    reminder_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus),
        default=NotificationStatus.NO_TIMER,
        nullable=False
    )

    def __str__(self):
        return (
            f"NotesOrm(id={self.id}, "
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"time_stamp={self.time_stamp}, "
            f"remind_after_minutes={self.remind_after_minutes}, "
            f"status={self.status})"
        )