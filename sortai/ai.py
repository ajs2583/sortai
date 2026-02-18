"""Gemini API client: build prompt from file list, call model, parse JSON moves."""

import json
import os
import re
from typing import Any

GEMINI_API_KEY_URL = "https://aistudio.google.com/app/apikey"


def list_available_models() -> list[str]:
    """List available Gemini models for the current API key."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        return []
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key.strip())
        models = client.models.list()
        model_names = []
        for m in models:
            if hasattr(m, "name"):
                name = m.name.split("/")[-1] if "/" in m.name else m.name
                model_names.append(name)
        return model_names
    except Exception:
        return []


class MissingApiKeyError(Exception):
    """Raised when GEMINI_API_KEY is not set."""

    def __init__(self) -> None:
        super().__init__(
            "GEMINI_API_KEY is not set. Get an API key at " + GEMINI_API_KEY_URL
        )


def get_moves(
    file_list: list[dict],
    depth: int,
    model_name: str = "gemini-2.5-flash",
) -> list[tuple[str, str]]:
    """
    Call Gemini to suggest folder structure. Returns list of (relative_path, target_folder).
    target_folder may be "." for root or e.g. "documents" or "documents/work" when depth > 1.
    Raises MissingApiKeyError if GEMINI_API_KEY is not set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise MissingApiKeyError()

    try:
        from google import genai
    except ImportError:
        raise ImportError(
            "google-genai package not installed. Run: pip install google-genai"
        )
    
    client = genai.Client(api_key=api_key.strip())
    prompt = _build_prompt(file_list, depth)
    
    # Try common model name variations
    model_variations = [
        model_name,
        f"models/{model_name}",
        f"publishers/google/models/{model_name}",
    ]
    
    last_error = None
    for model_variant in model_variations:
        try:
            response = client.models.generate_content(
                model=model_variant,
                contents=prompt,
            )
            text = (response.text or "").strip()
            return _parse_moves(text, file_list)
        except Exception as e:
            last_error = e
            if "404" not in str(e) and "not found" not in str(e).lower():
                # Not a 404, re-raise immediately
                raise
    
    # If all variations failed, try to list available models
    if "404" in str(last_error) or "not found" in str(last_error).lower():
        available = list_available_models()
        if available:
            raise ValueError(
                f"Model '{model_name}' not found. Available models: {', '.join(available[:10])}"
            )
        else:
            raise ValueError(
                f"Model '{model_name}' not found. Common models: gemini-1.5-flash, gemini-1.5-pro, gemini-2.5-flash"
            ) from last_error
    raise last_error
    


def _build_prompt(file_list: list[dict], depth: int) -> str:
    """Build the prompt for Gemini with file list and depth rules."""
    lines = [
        "You are organizing files in a directory. Given the list of files below (with optional content previews), suggest a folder structure.",
        "",
        "Rules:",
        "- Use only the relative paths exactly as given in the file list.",
        f"- Maximum folder depth is {depth}. So target_folder must be at most {depth} path segments (e.g. for depth 1 use a single folder name like 'documents'; for depth 2 you can use 'documents/work').",
        "- Use forward slashes in target_folder (e.g. 'documents/work').",
        "- To leave a file at the root, use target_folder: '.'.",
        "- Do not suggest moving outside the given directory or using absolute paths.",
        "- Output ONLY a single JSON object, no other text. Format:",
        '{"moves": [{"path": "filename.txt", "target_folder": "documents"}, ...]}',
        "",
        "File list:",
    ]
    for item in file_list:
        path = item.get("path", "")
        preview = item.get("content_preview")
        if preview:
            lines.append(f"- {path}")
            lines.append(f"  content_preview: {preview!r}")
        else:
            lines.append(f"- {path} (filename/extension only)")
    return "\n".join(lines)


def _parse_moves(response_text: str, file_list: list[dict]) -> list[tuple[str, str]]:
    """Extract JSON from response, validate paths against file_list, return list of (path, target_folder)."""
    valid_paths = {item["path"] for item in file_list}

    # Strip markdown code fences if present
    text = response_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    # Try raw parse in case there's no fence
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    moves_raw = data.get("moves")
    if not isinstance(moves_raw, list):
        return []

    result = []
    for entry in moves_raw:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        target = entry.get("target_folder")
        if path is None or target is None:
            continue
        path = str(path).strip()
        target = str(target).strip().replace("\\", "/")
        if path not in valid_paths:
            continue
        if not target:
            target = "."
        result.append((path, target))
    return result
