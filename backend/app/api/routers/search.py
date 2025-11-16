"""
Search and knowledge assistant endpoints.

This router provides a semantic search endpoint powered by the RAG pipeline.  It
returns summarised answers and extracted tasks based on the user's query.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ...core.cache import cache_get, cache_set, get_cache_key
from ...core.database import get_db
from ..deps import get_current_user
from ...services.rag_service import query_assistant


router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def semantic_search(
    request: Request,
    q: str = Query(..., min_length=1, description="The natural language query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results to retrieve"),
    start_date: Optional[str] = Query(None, description="Filter notes from this date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter notes until this date (ISO format)"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by"),
    keyword_search: bool = Query(False, description="Also perform keyword search and combine results"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """Perform semantic search across the current tenant's notes.

    The assistant retrieves relevant chunks, summarises them and extracts tasks.
    Users can only search their own notes unless they are tenant admins.
    
    Supports advanced filtering by date range and tags, and can combine
    semantic search with keyword search for better results.
    
    Rate limited: 100 requests per hour per user, 1000 per hour per tenant.
    """
    # Store current_user in request state for rate limiting
    request.state.current_user = current_user
    
    user_id = None if current_user.role == "admin" else str(current_user.id)
    
    # Check cache first
    cache_key = get_cache_key(
        "search",
        tenant_id=str(current_user.tenant_id),
        user_id=user_id or "",
        query=q,
        top_k=top_k,
        start_date=start_date or "",
        end_date=end_date or "",
        tags=tags or "",
        keyword_search=keyword_search,
    )
    
    cached_result = cache_get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        result = query_assistant(
            db,
            tenant_id=str(current_user.tenant_id),
            query=q,
            user_id=user_id,
            top_k=top_k,
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            keyword_search=keyword_search,
        )
        
        # Cache result for 5 minutes
        cache_set(cache_key, result, ttl=300)
        
        return result
    except RuntimeError as exc:
        # Missing configuration such as API key
        raise HTTPException(status_code=500, detail=str(exc))