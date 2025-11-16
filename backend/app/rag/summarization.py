"""
Summarisation utilities using LLMs.

This module wraps the OpenAI ChatCompletion API to summarise one or more
documents.  It accepts a list of text chunks and an optional query and returns
a concise summary.  If an OpenAI API key is not configured, a fallback
summarisation is performed by truncating the input.
"""
from typing import List, Optional

import openai

from ..core.config import settings


def summarise(chunks: List[str], query: Optional[str] = None) -> str:
    """Generate a summary from a list of text chunks.

    Args:
        chunks: List of text segments to summarise.
        query: Optional question or focus for the summary.
    Returns:
        A summary string.
    """
    # Concatenate chunks; we may truncate long inputs for token limits
    combined = "\n".join(chunks)
    if not settings.openai_api_key:
        # Fallback: return first 200 characters as a pseudo‑summary
        return (combined[:200] + "...") if len(combined) > 200 else combined
    
    # Use newer OpenAI client API
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    system_prompt = "You are a helpful assistant that summarises diary entries."
    if query:
        user_prompt = f"Summarise the following text with respect to the question: '{query}'."\
                      f"\n\nText:\n{combined}"
    else:
        user_prompt = f"Summarise the following diary entries in a concise paragraph.\n\nText:\n{combined}"
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=200,
    )
    summary = response.choices[0].message.content
    return summary.strip() if summary else combined[:200]