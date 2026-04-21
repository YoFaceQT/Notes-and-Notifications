from typing import List, Dict

from fastapi import APIRouter, HTTPException, status
from src.api.repository import TaskRepository
from src.schemas.schemas import TaskCreate, TaskUpdate, TaskSchema

router = APIRouter(prefix='/tasks')


@router.post('', status_code=status.HTTP_201_CREATED)
def add_note(note: TaskCreate)-> Dict[str, int]:
    note_id = TaskRepository.create_note(note)
    return {"task_id": note_id}


@router.get('')
def get_notes() -> List[TaskSchema]:
    notes = TaskRepository.show_notes()
    return notes


@router.patch('/{note_id}', status_code=status.HTTP_200_OK)
def update_note(note_id: int, note_update: TaskUpdate):
    updated_data = note_update.model_dump(exclude_unset=True)
    updated_id = TaskRepository.update_note(note_id, **updated_data)
    return updated_id


@router.delete('/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int)-> None:
    try:
        deleted_id = TaskRepository.delete_note(note_id)
        return {"deleted_task_id": deleted_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
