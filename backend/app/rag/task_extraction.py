"""
Task extraction using LLMs or heuristics.

This module provides a function to extract actionable tasks from a set of
strings (e.g. diary entry chunks).  The default implementation uses OpenAI
ChatCompletion to identify tasks and due dates.  If no API key is configured,
a simple heuristic is used to extract lines that appear to be tasks.
"""
import re
from datetime import datetime
from typing import Dict, List

import openai

from ..core.config import settings


def extract_tasks(chunks: List[str]) -> List[Dict[str, str | None]]:
    """Extract tasks from text chunks.

    Args:
        chunks: A list of text segments.
    Returns:
        A list of dicts with keys: description, due_date (ISO format or None).
    """
    text = "\n".join(chunks)
    tasks: List[Dict[str, str | None]] = []
    if not settings.openai_api_key:
        # Heuristic: extract lines beginning with common prefixes
        pattern = re.compile(r"^(?:TODO|Action item|Task)[:\-]\s*(.+)$", re.IGNORECASE | re.MULTILINE)
        for match in pattern.finditer(text):
            tasks.append({"description": match.group(1).strip(), "due_date": None})
        return tasks
    # Use newer OpenAI client API
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    system_prompt = "You extract actionable tasks from meeting notes or diary entries. " \
                    "Return a JSON array where each item has 'description' and optional 'due_date' (ISO format)." \
                    "If no due date is specified, set it to null."
    user_prompt = f"Extract tasks from the following text:\n\n{text}\n\nReturn JSON only."
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=200,
    )
    content = response.choices[0].message.content or ""
    # The model returns JSON; we attempt to parse it
    # Sometimes the response includes markdown code blocks, so we extract JSON from them
    import json
    import re
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    else:
        # Try to find JSON array in the content
        json_match = re.search(r'(\[.*?\])', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
    
    try:
        parsed = json.loads(content.strip())
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    tasks.append({
                        "description": item.get("description", "").strip(),
                        "due_date": item.get("due_date"),
                    })
                elif isinstance(item, str):
                    tasks.append({"description": item.strip(), "due_date": None})
        elif isinstance(parsed, dict):
            # Single task object
            tasks.append({
                "description": parsed.get("description", "").strip(),
                "due_date": parsed.get("due_date"),
            })
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        # Fallback: try to extract tasks using heuristics
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                # Remove bullet points
                line = re.sub(r'^[-*•]\s*', '', line)
                if line:
                    tasks.append({"description": line, "due_date": None})
        # If still no tasks, treat entire content as one task
        if not tasks:
            tasks.append({"description": content.strip(), "due_date": None})
    return tasks