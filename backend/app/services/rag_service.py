"""
High‑level service wrapping semantic search, summarisation and task extraction.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.note import Note
from ..models.task import Task, TaskStatus
from ..rag import faiss_index
from ..rag.summarization import summarise
from ..rag.task_extraction import extract_tasks
from ..rag.utils import split_text


def query_assistant(
    db: Session,
    tenant_id: str,
    query: str,
    user_id: Optional[str] = None,
    top_k: int = 5,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[str] = None,
    keyword_search: bool = False,
) -> Dict[str, any]:
    """Perform semantic search and generate a summarised answer with tasks.

    Args:
        db: Database session.
        tenant_id: Current tenant ID.
        query: Natural language question from the user.
        user_id: Optional user ID to filter results.
        top_k: Number of chunks to retrieve.
        start_date: Optional start date filter (ISO format string).
        end_date: Optional end date filter (ISO format string).
        tags: Optional comma-separated tags to filter by.
        keyword_search: If True, also perform keyword search and combine results.
    Returns:
        A dictionary with keys: `answer` (summary string),
        `chunks` (list of chunk texts with metadata) and `tasks` (extracted tasks).
    """
    # Build filters
    filters: Dict[str, Any] = {}
    if user_id:
        filters["user_id"] = user_id
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    if tags:
        filters["tags"] = tags
    
    # Perform semantic search
    try:
        semantic_results = faiss_index.semantic_search(tenant_id, query, top_k=top_k, filters=filters if filters else None)
    except ValueError:
        # Index does not exist; no search results
        semantic_results = []
    
    # Optionally perform keyword search and combine
    keyword_results = []
    if keyword_search:
        keyword_results = _keyword_search(db, tenant_id, query, user_id, start_date, end_date, tags, top_k)
    
    # Combine and deduplicate results
    search_results = _combine_search_results(semantic_results, keyword_results, top_k)
    
    chunk_texts: List[str] = []
    # Track note_ids from search results to link tasks
    note_ids_seen = set()
    for res in search_results:
        chunk_texts.append(res.get("text", ""))
        note_id = res.get("note_id")
        if note_id:
            note_ids_seen.add(note_id)
    
    if not chunk_texts:
        answer = "No relevant notes found."
        tasks: List[Dict[str, str | None]] = []
    else:
        answer = summarise(chunk_texts, query)
        extracted_tasks = extract_tasks(chunk_texts)
        
        # Save extracted tasks to database
        tasks = _save_tasks_to_db(db, tenant_id, user_id, extracted_tasks, note_ids_seen)
    
    return {
        "answer": answer,
        "chunks": search_results,
        "tasks": tasks,
    }


def _save_tasks_to_db(
    db: Session,
    tenant_id: str,
    user_id: Optional[str],
    extracted_tasks: List[Dict[str, str | None]],
    note_ids: set,
) -> List[Dict[str, str | None]]:
    """Save extracted tasks to the database and return them.
    
    Args:
        db: Database session.
        tenant_id: Tenant ID.
        user_id: User ID (optional, for filtering).
        extracted_tasks: List of extracted task dictionaries.
        note_ids: Set of note IDs from search results.
    Returns:
        List of task dictionaries (same format as extracted_tasks).
    """
    saved_tasks = []
    
    if not extracted_tasks or not note_ids:
        return extracted_tasks
    
    # Convert note_ids to UUIDs
    note_uuids = []
    for note_id_str in note_ids:
        try:
            note_uuids.append(UUID(note_id_str))
        except (ValueError, TypeError):
            continue
    
    if not note_uuids:
        return extracted_tasks
    
    # Get the first note_id to link tasks (or distribute across notes)
    primary_note_id = note_uuids[0]
    
    for task_data in extracted_tasks:
        description = task_data.get("description", "").strip()
        if not description:
            continue
        
        # Parse due_date if provided
        due_date = None
        due_date_str = task_data.get("due_date")
        if due_date_str:
            try:
                # Try parsing ISO format
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    # Try parsing other common formats
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                except (ValueError, AttributeError):
                    due_date = None
        
        # Check if task already exists (avoid duplicates)
        existing = db.query(Task).filter(
            Task.tenant_id == UUID(tenant_id),
            Task.note_id == primary_note_id,
            Task.description == description,
            Task.status == TaskStatus.open.value
        ).first()
        
        if existing:
            # Task already exists, skip
            saved_tasks.append({
                "description": description,
                "due_date": due_date_str if due_date_str else None,
            })
            continue
        
        # Determine user_id for the task
        task_user_id = UUID(user_id) if user_id else None
        if not task_user_id:
            # If no user_id provided, get from note
            note = db.query(Note).filter(Note.id == primary_note_id).first()
            if note:
                task_user_id = note.user_id
            else:
                # Skip if we can't determine user_id
                saved_tasks.append({
                    "description": description,
                    "due_date": due_date_str if due_date_str else None,
                })
                continue
        
        # Create new task
        new_task = Task(
            tenant_id=UUID(tenant_id),
            user_id=task_user_id,
            note_id=primary_note_id,
            description=description,
            due_date=due_date,
            status=TaskStatus.open.value,
        )
        db.add(new_task)
        saved_tasks.append({
            "description": description,
            "due_date": due_date_str if due_date_str else None,
        })
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # Return extracted tasks even if save fails
        return extracted_tasks
    
    return saved_tasks


def _keyword_search(
    db: Session,
    tenant_id: str,
    query: str,
    user_id: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    tags: Optional[str],
    top_k: int,
) -> List[Dict[str, Any]]:
    """Perform keyword-based search on notes.
    
    Args:
        db: Database session.
        tenant_id: Tenant ID.
        query: Search query.
        user_id: Optional user ID filter.
        start_date: Optional start date filter.
        end_date: Optional end date filter.
        tags: Optional tags filter.
        top_k: Number of results to return.
    Returns:
        List of chunk dictionaries with metadata.
    """
    # Build database query
    db_query = db.query(Note).filter(Note.tenant_id == UUID(tenant_id))
    
    if user_id:
        db_query = db_query.filter(Note.user_id == UUID(user_id))
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            db_query = db_query.filter(Note.created_at >= start_dt)
        except (ValueError, AttributeError):
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            db_query = db_query.filter(Note.created_at <= end_dt)
        except (ValueError, AttributeError):
            pass
    
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        db_query = db_query.filter(Note.tags.contains(tag_list))
    
    # Search in title and content
    query_terms = query.lower().split()
    conditions = []
    for term in query_terms:
        conditions.append(Note.title.ilike(f"%{term}%"))
        conditions.append(Note.content.ilike(f"%{term}%"))
    
    if conditions:
        db_query = db_query.filter(or_(*conditions))
    
    notes = db_query.limit(top_k * 2).all()  # Get more notes to chunk
    
    # Convert notes to chunks
    results = []
    for note in notes:
        if not note.content:
            continue
        
        chunks = split_text(note.content)
        for chunk in chunks:
            if not chunk.strip():
                continue
            
            # Simple relevance scoring based on term matches
            chunk_lower = chunk.lower()
            score = sum(1 for term in query_terms if term in chunk_lower) / len(query_terms) if query_terms else 0
            
            results.append({
                "note_id": str(note.id),
                "user_id": str(note.user_id),
                "tenant_id": tenant_id,
                "text": chunk,
                "score": score,
                "created_at": note.created_at.isoformat() if note.created_at else None,
                "tags": note.tags if note.tags else [],
            })
    
    # Sort by score and return top_k
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:top_k]


def _combine_search_results(
    semantic_results: List[Dict[str, Any]],
    keyword_results: List[Dict[str, Any]],
    top_k: int,
) -> List[Dict[str, Any]]:
    """Combine semantic and keyword search results, deduplicating by note_id+text.
    
    Args:
        semantic_results: Results from semantic search.
        keyword_results: Results from keyword search.
        top_k: Maximum number of results to return.
    Returns:
        Combined and deduplicated results.
    """
    if not keyword_results:
        return semantic_results[:top_k]
    
    # Create a set of seen chunks (by note_id + text hash)
    seen = set()
    combined = []
    
    # Add semantic results first (they're already sorted by relevance)
    for result in semantic_results:
        chunk_key = (result.get("note_id"), hash(result.get("text", "")))
        if chunk_key not in seen:
            seen.add(chunk_key)
            combined.append(result)
            if len(combined) >= top_k:
                return combined
    
    # Add keyword results that aren't duplicates
    for result in keyword_results:
        chunk_key = (result.get("note_id"), hash(result.get("text", "")))
        if chunk_key not in seen:
            seen.add(chunk_key)
            combined.append(result)
            if len(combined) >= top_k:
                return combined
    
    return combined