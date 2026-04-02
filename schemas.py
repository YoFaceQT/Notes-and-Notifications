"""
Модуль с моделями Pydantic для управления задачами.

Содержит модель Task с валидацией полей и преобразованием типов.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from constants import DESCRIPTION_MAX_LENGHT, NAME_MAX_LENGHT, NAME_MIN_LENGHT
from models import NotificationStatus


class TaskBase(BaseModel):
    name: str = Field(
        ...,
        min_length=NAME_MIN_LENGHT,
        max_length=NAME_MAX_LENGHT
    )
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGHT)
    remind_after_minutes: Optional[int] = Field(None, ge=1)


class CommonValidatorsMixin:
    """Миксин с общими валидаторами для полей name и description."""

    @field_validator('name', mode='before')
    @classmethod
    def normalize_name(cls, v):
        if isinstance(v, int):
            v = str(v)
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                raise ValueError('Название не может быть пустым')
            return v
        if v is None:
            return v
        raise ValueError('Название должно быть строкой или числом')

    @field_validator('description', mode='before')
    @classmethod
    def normalize_description(cls, v):
        if isinstance(v, (int, str, type(None))):
            return str(v) if isinstance(v, int) else v
        raise ValueError('Описание должно быть строкой, числом или None')


class TaskCreate(TaskBase, CommonValidatorsMixin):
    status: NotificationStatus = Field(default=NotificationStatus.NO_TIMER)

    @model_validator(mode='after')
    def set_status_by_timer(self) -> 'TaskCreate':
        if self.remind_after_minutes is not None:
            self.status = NotificationStatus.IN_PROGRESS
        else:
            self.status = NotificationStatus.NO_TIMER
        return self


class TaskSchema(TaskBase):
    id: int
    time_stamp: datetime = Field(default_factory=datetime.now)
    reminded: bool = Field(default=False)

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel, CommonValidatorsMixin):
    name: Optional[str] = Field(None, min_length=NAME_MIN_LENGHT, max_length=NAME_MAX_LENGHT)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGHT)
    remind_after_minutes: Optional[int] = Field(None, ge=1)