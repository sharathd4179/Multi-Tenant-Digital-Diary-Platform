"""
Build FAISS indexes inside the Docker backend container.
This script can be run directly in the container.
"""
import os
import sys
import pickle
from typing import Dict, List

import openai
import sqlalchemy as sa
from sqlalchemy.orm import Session

import faiss
import numpy as np

# Add app to path
sys.path.insert(0, '/app')

# Import all models to ensure relationships are set up
from app.models import base as base_model
from app.models import tenant as tenant_model
from app.models import user as user_model  # Import User to fix relationship
from app.models import note as note_model
from app.models import task as task_model  # Import Task to fix relationship
from app.core.config import settings
from app.rag.utils import split_text


def get_embedding(text: str) -> List[float]:
    """Get embedding from OpenAI."""
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    
    # Use OpenAI client (newer API)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except ImportError:
        # Fallback to old API
        openai.api_key = settings.openai_api_key
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        return response["data"][0]["embedding"]


def build_index_for_tenant(session: Session, tenant_id: str, notes: List[note_model.Note]) -> None:
    """Build FAISS index for a tenant's notes."""
    vectors = []
    metadata = []
    
    print(f"Processing {len(notes)} notes for tenant {tenant_id}...")
    
    for note in notes:
        if not note.content:
            continue
        chunks = split_text(note.content)
        for chunk in chunks:
            if not chunk.strip():
                continue
            try:
                emb = get_embedding(chunk)
                vectors.append(emb)
                metadata.append({
                    "note_id": str(note.id),
                    "user_id": str(note.user_id),
                    "tenant_id": tenant_id,
                    "text": chunk,
                })
            except Exception as e:
                print(f"Error getting embedding: {e}")
                continue

    if not vectors:
        print(f"No vectors generated for tenant {tenant_id}")
        return

    dim = len(vectors[0])
    vectors_np = np.array(vectors, dtype=np.float32)
    
    # Build HNSW index
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
    
    print(f"✅ Built index for tenant {tenant_id}: {len(vectors)} vectors")
    print(f"   Index saved: {idx_path}")
    print(f"   Metadata saved: {meta_path}")


def main():
    """Main function to build indexes."""
    print("=" * 60)
    print("Building FAISS Indexes for Semantic Search")
    print("=" * 60)
    print()
    
    if not settings.openai_api_key:
        print("❌ ERROR: OPENAI_API_KEY not configured!")
        print("   Set it in your .env file or environment variables.")
        return
    
    db_url = settings.database_url
    print(f"Connecting to database: {db_url.split('@')[1] if '@' in db_url else '***'}")
    
    engine = sa.create_engine(db_url)
    base_model.Base.metadata.create_all(bind=engine)
    session = Session(engine)

    tenants = session.query(tenant_model.Tenant).all()
    print(f"\nFound {len(tenants)} tenant(s)")
    print()
    
    for tenant in tenants:
        notes = session.query(note_model.Note).filter(
            note_model.Note.tenant_id == tenant.id
        ).all()
        
        if not notes:
            print(f"⚠️  Tenant {tenant.name} ({tenant.id}) has no notes. Skipping.")
            continue
        
        build_index_for_tenant(session, str(tenant.id), notes)
        print()

    session.close()
    print("=" * 60)
    print("✅ Index building complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

