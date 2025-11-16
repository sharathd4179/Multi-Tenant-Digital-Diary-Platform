"""
Script to build FAISS HNSW indexes for each tenant.

This script reads notes from the database, generates embeddings using the OpenAI
API (or any embedding function) and builds a FAISS index per tenant using the
HNSW algorithm.  Each index is saved on disk under the `vector_indexes/`
directory.  When the backend starts, it will load these indexes on demand.

Usage:

```
python scripts/create_faiss_index.py --db-url=<db-url> --openai-api-key=<key>
```
"""
import argparse
import os
import pickle
from typing import Dict, List

import openai
import sqlalchemy as sa
from sqlalchemy.orm import Session

import faiss
import numpy as np

from backend.app.models import note as note_model
from backend.app.models import user as user_model
from backend.app.models import tenant as tenant_model
from backend.app.core.config import Settings
from backend.app.rag.utils import split_text


def parse_args():
    parser = argparse.ArgumentParser(description="Build FAISS HNSW index")
    parser.add_argument("--db-url", required=False, default=os.getenv("DATABASE_URL"), help="Database URL")
    parser.add_argument("--openai-api-key", required=False, default=os.getenv("OPENAI_API_KEY"), help="OpenAI API key")
    return parser.parse_args()


def get_embedding(text: str) -> List[float]:
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response["data"][0]["embedding"]  # type: ignore


def build_index_for_tenant(session: Session, tenant_id: str, notes: List[note_model.Note]) -> None:
    vectors = []
    metadata = []
    for note in notes:
        chunks = split_text(note.content or "")
        for chunk in chunks:
            emb = get_embedding(chunk)
            vectors.append(emb)
            metadata.append({
                "note_id": str(note.id),
                "user_id": str(note.user_id),
                "tenant_id": tenant_id,
                "text": chunk,
            })

    if not vectors:
        return

    dim = len(vectors[0])
    vectors_np = np.array(vectors, dtype=np.float32)
    # Build HNSW index
    index = faiss.IndexHNSWFlat(dim, 32)  # M=32 by default
    index.hnsw.efConstruction = 200
    index.add(vectors_np)

    # Save index and metadata
    os.makedirs("vector_indexes", exist_ok=True)
    faiss.write_index(index, f"vector_indexes/index_{tenant_id}.faiss")
    with open(f"vector_indexes/metadata_{tenant_id}.pkl", "wb") as f:
        pickle.dump(metadata, f)


def main():
    args = parse_args()
    openai.api_key = args.openai_api_key

    engine = sa.create_engine(args.db_url)
    session = Session(engine)

    tenants = session.query(tenant_model.Tenant).all()
    for tenant in tenants:
        notes = session.query(note_model.Note).filter(note_model.Note.tenant_id == tenant.id).all()
        build_index_for_tenant(session, str(tenant.id), notes)
        print(f"Built FAISS index for tenant {tenant.name} ({tenant.id}) with {len(notes)} notes")

    session.close()


if __name__ == "__main__":
    main()