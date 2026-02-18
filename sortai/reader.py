"""File listing and content extraction (first ~500 chars) for text-based types."""

import os
from pathlib import Path
from typing import Optional

CONTENT_PREVIEW_LENGTH = 500

# Extensions for which we read file content; everything else is categorized by filename/extension only.
CONTENT_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".csv"}


def _read_text_preview(path: Path, limit: int = CONTENT_PREVIEW_LENGTH) -> Optional[str]:
    """Read first `limit` characters from a text file. Returns None on error."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return (f.read(limit + 1))[:limit] or None
    except OSError:
        return None


def _read_pdf_preview(path: Path, limit: int = CONTENT_PREVIEW_LENGTH) -> Optional[str]:
    """Extract text from first page of PDF and truncate. Returns None on error."""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            if not pdf.pages:
                return None
            text = pdf.pages[0].extract_text()
            if not text:
                return None
            return (text[: limit + 1])[:limit]
    except Exception:
        return None


def _read_docx_preview(path: Path, limit: int = CONTENT_PREVIEW_LENGTH) -> Optional[str]:
    """Extract paragraph text from docx and truncate. Returns None on error."""
    try:
        from docx import Document
        doc = Document(path)
        parts = []
        n = 0
        for para in doc.paragraphs:
            if para.text:
                parts.append(para.text)
                n += len(para.text)
                if n >= limit:
                    break
        text = " ".join(parts)
        return (text[: limit + 1])[:limit] if text else None
    except Exception:
        return None


def get_content_preview(path: Path, limit: int = CONTENT_PREVIEW_LENGTH) -> Optional[str]:
    """Return first ~limit characters of file content for supported types, else None."""
    ext = path.suffix.lower()
    if ext in (".txt", ".md", ".csv"):
        return _read_text_preview(path, limit)
    if ext == ".pdf":
        return _read_pdf_preview(path, limit)
    if ext == ".docx":
        return _read_docx_preview(path, limit)
    return None


def list_files(
    root: Path,
    max_depth: Optional[int] = None,
) -> list[dict]:
    """
    Walk directory up to max_depth levels; return list of dicts with path (relative),
    name (filename), and content_preview (first ~500 chars for supported types, else None).
    """
    root = root.resolve()
    if not root.is_dir():
        return []

    result = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath = Path(dirpath)
        depth = len(dirpath.relative_to(root).parts) if dirpath != root else 0
        if max_depth is not None and depth > max_depth:
            continue
        if max_depth is not None and depth >= max_depth:
            dirnames[:] = []  # do not descend further
        for name in filenames:
            full_path = dirpath / name
            try:
                rel = full_path.relative_to(root)
            except ValueError:
                continue
            rel_str = str(rel).replace("\\", "/")
            content = get_content_preview(full_path) if full_path.suffix.lower() in CONTENT_EXTENSIONS else None
            result.append({
                "path": rel_str,
                "name": name,
                "content_preview": content,
            })
    return result
