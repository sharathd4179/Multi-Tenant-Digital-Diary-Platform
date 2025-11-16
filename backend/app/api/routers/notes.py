"""
Endpoints for creating, reading, updating and deleting notes.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.cache import cache_get, cache_set, get_cache_key, cache_delete_pattern
from ...core.database import get_db
from ...models.note import Note
from ...schemas.note import NoteCreate, NoteRead, NoteUpdate
from ...services.index_service import rebuild_index_for_tenant
from ..deps import get_current_user, require_admin


router = APIRouter()


@router.get("/", response_model=List[NoteRead])
def list_notes(
    skip: int = 0,
    limit: int = 50,
    start_date: Optional[datetime] = Query(None, description="Filter notes from this date (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="Filter notes until this date (inclusive)"),
    tags: Optional[str] = Query(None, description="Comma‑separated list of tags to filter by"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[NoteRead]:
    """Return a list of notes for the current user's tenant.

    Admins see all notes in the tenant.  Normal users see only their own notes.
    Optional filters allow limiting by date range and tags.
    
    Results are cached for 1 minute to improve performance.
    """
    # Check cache
    cache_key = get_cache_key(
        "notes",
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id) if current_user.role != "admin" else "admin",
        skip=skip,
        limit=limit,
        start_date=start_date.isoformat() if start_date else "",
        end_date=end_date.isoformat() if end_date else "",
        tags=tags or "",
    )
    
    cached_result = cache_get(cache_key)
    if cached_result:
        return [NoteRead.model_validate(n) for n in cached_result]
    
    query = db.query(Note).filter(Note.tenant_id == current_user.tenant_id)
    if current_user.role != "admin":
        query = query.filter(Note.user_id == current_user.id)
    if start_date:
        query = query.filter(Note.created_at >= start_date)
    if end_date:
        query = query.filter(Note.created_at <= end_date)
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.filter(Note.tags.contains(tag_list))
    notes = query.offset(skip).limit(limit).all()
    
    # Cache result for 1 minute
    notes_dict = [NoteRead.model_validate(n).model_dump() for n in notes]
    cache_set(cache_key, notes_dict, ttl=60)
    
    return [NoteRead.model_validate(n) for n in notes]


@router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    note_in: NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> NoteRead:
    """Create a new note for the current user.

    The `tenant_id` and `user_id` in the request body must match the
    authenticated user and tenant.  Admins can create notes on behalf of other
    users within their tenant.
    
    After creation, the FAISS index is automatically rebuilt in the background.
    """
    if note_in.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant mismatch")
    if current_user.role != "admin" and note_in.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create notes for other users")
    note = Note(
        tenant_id=note_in.tenant_id,
        user_id=note_in.user_id,
        title=note_in.title,
        content=note_in.content,
        tags=note_in.tags,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # Invalidate cache for this tenant
    cache_delete_pattern(f"notes:tenant_id:{note_in.tenant_id}:*")
    cache_delete_pattern(f"search:tenant_id:{note_in.tenant_id}:*")
    
    # Rebuild index in background (note: don't pass db session to background task)
    background_tasks.add_task(rebuild_index_for_tenant, str(note_in.tenant_id))
    
    return NoteRead.model_validate(note)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> NoteRead:
    """Retrieve a single note by ID."""
    note = db.query(Note).filter(Note.id == note_id, Note.tenant_id == current_user.tenant_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    if current_user.role != "admin" and note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to view this note")
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: UUID,
    note_in: NoteUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> NoteRead:
    """Update a note. FAISS index is automatically rebuilt in the background."""
    note = db.query(Note).filter(Note.id == note_id, Note.tenant_id == current_user.tenant_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    if current_user.role != "admin" and note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to update this note")
    for field, value in note_in.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    
    # Invalidate cache for this tenant
    cache_delete_pattern(f"notes:tenant_id:{note.tenant_id}:*")
    cache_delete_pattern(f"search:tenant_id:{note.tenant_id}:*")
    
    # Rebuild index in background
    background_tasks.add_task(rebuild_index_for_tenant, str(note.tenant_id))
    
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
) -> None:
    """Delete a note. FAISS index is automatically rebuilt in the background."""
    note = db.query(Note).filter(Note.id == note_id, Note.tenant_id == current_user.tenant_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    if current_user.role != "admin" and note.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to delete this note")
    
    tenant_id = str(note.tenant_id)
    db.delete(note)
    db.commit()
    
    # Invalidate cache for this tenant
    cache_delete_pattern(f"notes:tenant_id:{tenant_id}:*")
    cache_delete_pattern(f"search:tenant_id:{tenant_id}:*")
    
    # Rebuild index in background
    background_tasks.add_task(rebuild_index_for_tenant, tenant_id)