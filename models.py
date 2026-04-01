"""
Модуль с моделями Pydantic для управления задачами.

Содержит модель Task с валидацией полей и преобразованием типов.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from constants import DESCRIPTION_MAX_LENGHT, NAME_MAX_LENGHT, NAME_MIN_LENGHT


class TaskSchema(BaseModel):
    """
    Модель задачи с валидацией данных.

    Attributes:
        id (int): Уникальный идентификатор задачи
        name (str): Название задачи (обязательное поле, до 40 символов)
        description (Optional[str]): Описание (опционально, до 256 символов)
        time_stamp (datetime): Временная метка создания задачи (автоматически)
    """

    id: int
    name: str = Field(
        ...,
        min_length=NAME_MIN_LENGHT,
        max_length=NAME_MAX_LENGHT
    )
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGHT)
    time_stamp: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(extra='forbid')

    @field_validator('name', mode='before')
    def name_to_str(cls, data) -> str:
        """Преобразует название заметки в строку."""

        if isinstance(data, int):
            return str(data)
        if isinstance(data, str):
            return data
        else:
            raise ValueError(
                'Название заметки должно быть строкой или числом'
            )

    @field_validator('name')
    def validate_not_empty(cls, v: str) -> str:
        """Проверяет, что название не пустое и не состоит из пробелов."""

        if not v or not v.strip():
            raise ValueError(
                'Поле не может быть пустым или состоять только из пробелов'
                )
        return v.strip()

    @field_validator('description', mode='before')
    def description_to_str(cls, data) -> Optional[str]:
        """Преобразует описание заметки в строку."""

        if isinstance(data, int):
            return str(data)
        if isinstance(data, str):
            return data
        if data is None:
            return data
        else:
            raise ValueError(
                'Описание заметки должно быть строкой или числом'
            )


class NotificationSchema(TaskSchema):
    """Модель уведомления наследуемая от модели Task"""
    minutes: int = Field(ge=0, le=60)
