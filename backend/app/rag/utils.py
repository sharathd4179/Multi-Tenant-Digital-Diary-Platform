"""
Utility functions for the RAG pipeline.
"""
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..core.config import settings


def split_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> List[str]:
    """Split a text into overlapping chunks.

    Args:
        text: The input string.
        chunk_size: Optional override for chunk size.
        overlap: Optional override for overlap between chunks.
    Returns:
        A list of text chunks.
    """
    size = chunk_size or settings.rag_chunk_size
    ov = overlap or settings.rag_overlap
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=ov)
    return splitter.split_text(text or "")