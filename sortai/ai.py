"""Gemini API client: build prompt from file list, call model, parse JSON moves."""

import json
import os
import re
from typing import Any

GEMINI_API_KEY_URL = "https://aistudio.google.com/app/apikey"


class MissingApiKeyError(Exception):
    """Raised when GEMINI_API_KEY is not set."""

    def __init__(self) -> None:
        super().__init__(
            "GEMINI_API_KEY is not set. Get an API key at " + GEMINI_API_KEY_URL
        )


def get_moves(
    file_list: list[dict],
    depth: int,
    model_name: str = "gemini-1.5-flash",
) -> list[tuple[str, str]]:
    """
    Call Gemini to suggest folder structure. Returns list of (relative_path, target_folder).
    target_folder may be "." for root or e.g. "documents" or "documents/work" when depth > 1.
    Raises MissingApiKeyError if GEMINI_API_KEY is not set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise MissingApiKeyError()

    import google.generativeai as genai
    genai.configure(api_key=api_key.strip())
    model = genai.GenerativeModel(model_name)

    prompt = _build_prompt(file_list, depth)
    response = model.generate_content(prompt)
    text = (response.text or "").strip()
    return _parse_moves(text, file_list)


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
