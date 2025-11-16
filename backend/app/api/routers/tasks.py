"""
Task management endpoints.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.task import Task
from ...schemas.task import TaskRead
from ..deps import get_current_user


router = APIRouter()


@router.get("/", response_model=List[TaskRead])
def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by task status (open/completed)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[TaskRead]:
    """Return tasks for the current user or tenant."""
    query = db.query(Task).filter(Task.tenant_id == current_user.tenant_id)
    if current_user.role != "admin":
        query = query.filter(Task.user_id == current_user.id)
    if status_filter:
        query = query.filter(Task.status == status_filter)
    tasks = query.all()
    return [TaskRead.model_validate(t) for t in tasks]


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TaskRead:
    """Mark a task as completed."""
    task = db.query(Task).filter(Task.id == task_id, Task.tenant_id == current_user.tenant_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role != "admin" and task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to modify this task")
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return TaskRead.model_validate(task)