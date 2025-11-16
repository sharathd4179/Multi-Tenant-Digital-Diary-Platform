"""
FAISS index management for semantic search.

This module provides functions to load HNSW indexes per tenant, compute query
embeddings and perform similarity search.  Indexes and metadata are stored in
the `vector_indexes/` directory and are loaded on demand.  If an index is
missing, a ValueError is raised.
"""
import os
import pickle
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import faiss
import numpy as np
import openai

from ..core.config import settings


# In‑memory cache for loaded FAISS indexes
_index_cache: Dict[str, Tuple[faiss.IndexHNSWFlat, List[Dict[str, Any]]]] = {}


def load_index(tenant_id: str) -> Tuple[faiss.IndexHNSWFlat, List[Dict[str, Any]]]:
    """Load FAISS index and metadata for a tenant.  Cache the result in memory."""
    if tenant_id in _index_cache:
        return _index_cache[tenant_id]
    idx_path = f"vector_indexes/index_{tenant_id}.faiss"
    meta_path = f"vector_indexes/metadata_{tenant_id}.pkl"
    if not os.path.exists(idx_path) or not os.path.exists(meta_path):
        raise ValueError(f"Index for tenant {tenant_id} not found; run create_faiss_index.py")
    index = faiss.read_index(idx_path)
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)
    _index_cache[tenant_id] = (index, metadata)
    return index, metadata


def compute_query_embedding(query: str) -> List[float]:
    """Compute an embedding vector for the query using OpenAI."""
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    
    # Use newer OpenAI client API (required for openai>=1.0.0)
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def semantic_search(tenant_id: str, query: str, top_k: int = 5, filters: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """Perform a similarity search over the tenant's FAISS index.

    Args:
        tenant_id: The tenant whose index to search.
        query: The raw user query.
        top_k: Number of results to return.
        filters: Optional metadata filters (e.g. user_id, date ranges, tags).
                 Supports:
                 - user_id: exact match
                 - start_date/end_date: date range filtering (ISO format strings)
                 - tags: list of tags (chunk matches if any tag in list)
    Returns:
        A list of metadata dictionaries for the top matching chunks, each with
        additional fields `score` and `chunk_text`.
    """
    from datetime import datetime
    
    index, metadata = load_index(tenant_id)
    query_vector = np.array([compute_query_embedding(query)], dtype=np.float32)
    # Search more results initially to account for filtering
    search_k = top_k * 3 if filters else top_k
    D, I = index.search(query_vector, min(search_k, len(metadata)))
    results: List[Dict[str, Any]] = []
    
    for score, idx in zip(D[0], I[0]):
        if idx >= len(metadata):
            continue
        meta = metadata[idx].copy()
        
        # Apply filters
        if filters:
            match = True
            
            # Exact match filters
            for key in ["user_id", "tenant_id"]:
                if key in filters and meta.get(key) != filters[key]:
                    match = False
                    break
            
            # Date range filtering
            if match and ("start_date" in filters or "end_date" in filters):
                created_at_str = meta.get("created_at")
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        if "start_date" in filters:
                            start_date = filters["start_date"]
                            if isinstance(start_date, str):
                                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                            if created_at < start_date:
                                match = False
                        if match and "end_date" in filters:
                            end_date = filters["end_date"]
                            if isinstance(end_date, str):
                                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                            if created_at > end_date:
                                match = False
                    except (ValueError, AttributeError):
                        # If date parsing fails, skip date filtering for this chunk
                        pass
            
            # Tag filtering (chunk matches if any tag in filter list is in note tags)
            if match and "tags" in filters:
                filter_tags = filters["tags"]
                if isinstance(filter_tags, str):
                    filter_tags = [t.strip() for t in filter_tags.split(",")]
                note_tags = meta.get("tags", [])
                if not isinstance(note_tags, list):
                    note_tags = []
                # Check if any filter tag is in note tags
                if not any(tag in note_tags for tag in filter_tags):
                    match = False
            
            if not match:
                continue
        
        meta["score"] = float(score)
        results.append(meta)
        
        # Stop when we have enough results
        if len(results) >= top_k:
            break
    
    return results