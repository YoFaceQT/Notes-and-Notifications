from typing import List

from fastapi import APIRouter, HTTPException

from src.api.repository import TaskRepository
from src.schemas.schemas import TaskCreate, TaskUpdate, TaskSchema

router = APIRouter(prefix='/tasks')


@router.post('')
def add_note(note: TaskCreate):
    note_id = TaskRepository.create_note(note)
    return {"task_id": note_id}


@router.get('')
def get_notes() -> List[TaskSchema]:
    notes = TaskRepository.show_notes()
    return notes


@router.patch('/{note_id}')
def update_note(note_id: int, note_update: TaskUpdate):
    updated_data = note_update.model_dump(exclude_unset=True)
    updated_id = TaskRepository.update_note(note_id, **updated_data)
    return updated_id


@router.delete('/{note_id}')
def delete_note(note_id: int):
    try:
        deleted_id = TaskRepository.delete_note(note_id)
        return {"deleted_task_id": deleted_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
