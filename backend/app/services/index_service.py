"""
Service for managing FAISS index updates.

This service handles automatic index rebuilding when notes are created, updated, or deleted.
It uses background tasks to avoid blocking API responses.
"""
import os
import pickle
from typing import List

import faiss
import numpy as np
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import SessionLocal
from ..models.note import Note
from ..rag.faiss_index import compute_query_embedding
from ..rag.utils import split_text


def rebuild_index_for_tenant(tenant_id: str) -> bool:
    """Rebuild the FAISS index for a specific tenant.
    
    This function creates its own database session for use in background tasks.
    It should be called from FastAPI BackgroundTasks, not directly with a db session.
    
    Args:
        tenant_id: Tenant UUID as string.
    Returns:
        True if successful, False otherwise.
    """
    db = SessionLocal()
    try:
        # Get all notes for this tenant
        notes = db.query(Note).filter(Note.tenant_id == tenant_id).all()
        
        if not notes:
            # No notes, but we should still create an empty index or remove old one
            _remove_index(tenant_id)
            return True
        
        vectors = []
        metadata = []
        
        for note in notes:
            if not note.content:
                continue
            
            chunks = split_text(note.content)
            for chunk in chunks:
                if not chunk.strip():
                    continue
                
                try:
                    emb = compute_query_embedding(chunk)
                    vectors.append(emb)
                    # Include date and tags in metadata for filtering
                    metadata.append({
                        "note_id": str(note.id),
                        "user_id": str(note.user_id),
                        "tenant_id": tenant_id,
                        "text": chunk,
                        "created_at": note.created_at.isoformat() if note.created_at else None,
                        "tags": note.tags if note.tags else [],
                    })
                except Exception as e:
                    # Log error but continue with other chunks
                    print(f"Error generating embedding for chunk: {e}")
                    continue
        
        if not vectors:
            _remove_index(tenant_id)
            return True
        
        # Build HNSW index
        dim = len(vectors[0])
        vectors_np = np.array(vectors, dtype=np.float32)
        index = faiss.IndexHNSWFlat(dim, 32)  # M=32
        index.hnsw.efConstruction = 200
        index.add(vectors_np)
        
        # Save index and metadata
        os.makedirs("vector_indexes", exist_ok=True)
        idx_path = f"vector_indexes/index_{tenant_id}.faiss"
        meta_path = f"vector_indexes/metadata_{tenant_id}.pkl"
        
        faiss.write_index(index, idx_path)
        with open(meta_path, "wb") as f:
            pickle.dump(metadata, f)
        
        # Clear cache so new index is loaded
        from ..rag.faiss_index import _index_cache
        if tenant_id in _index_cache:
            del _index_cache[tenant_id]
        
        return True
        
    except Exception as e:
        print(f"Error rebuilding index for tenant {tenant_id}: {e}")
        return False
    finally:
        db.close()


def _remove_index(tenant_id: str) -> None:
    """Remove index files for a tenant."""
    idx_path = f"vector_indexes/index_{tenant_id}.faiss"
    meta_path = f"vector_indexes/metadata_{tenant_id}.pkl"
    
    try:
        if os.path.exists(idx_path):
            os.remove(idx_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
        
        # Clear cache
        from ..rag.faiss_index import _index_cache
        if tenant_id in _index_cache:
            del _index_cache[tenant_id]
    except Exception:
        pass  # Ignore errors when removing

