from typing import List

from fastapi import APIRouter, HTTPException, status

from src.api.repository import TaskRepository
from src.schemas.schemas import TaskCreate, TaskUpdate, TaskSchema


router = APIRouter(prefix='/tasks')


@router.post('', status_code=status.HTTP_201_CREATED)
async def add_note(note: TaskCreate) -> TaskSchema:
    """Создаёт заметку и возвращает созданную запись."""
    return await TaskRepository.create_note(note)


@router.get('')
async def get_notes() -> List[TaskSchema]:
    """Возвращает список всех заметок."""
    return await TaskRepository.show_notes()


@router.patch('/{note_id}', status_code=status.HTTP_200_OK)
async def update_note(note_id: int, note_update: TaskUpdate) -> TaskSchema:
    """Обновляет заметку и возвращает обновлённую запись."""
    updated = await TaskRepository.update_note(
        note_id,
        **note_update.model_dump(exclude_unset=True)
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated


@router.delete('/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int) -> None:
    """Удаляет заметку. Возвращает статус 204 без тела."""
    try:
        await TaskRepository.delete_note(note_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
