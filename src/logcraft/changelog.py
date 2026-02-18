"""Changelog generation: categorize commits and render Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator

# Conventional commit prefix -> section title (case-insensitive)
PREFIX_TO_CATEGORY = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "chore": "Maintenance",
}

CATEGORY_ORDER = ["Features", "Bug Fixes", "Maintenance", "Other"]


@dataclass
class CommitEntry:
    """One line in the changelog."""

    short_hash: str
    date: str  # YYYY-MM-DD
    subject: str
    category: str


def _categorize(subject: str) -> str:
    """Return category for the commit subject (first line)."""
    subject_lower = subject.strip().lower()
    for prefix, category in PREFIX_TO_CATEGORY.items():
        if subject_lower.startswith(prefix + ":") or subject_lower.startswith(prefix + "("):
            return category
    return "Other"


def _subject_display(subject: str, category: str) -> str:
    """Return subject line for display; optionally strip conventional prefix."""
    subject = subject.strip()
    subject_lower = subject.lower()
    for prefix in PREFIX_TO_CATEGORY:
        if subject_lower.startswith(prefix + ":"):
            rest = subject[len(prefix) + 1 :].lstrip()
            return rest or subject
        if subject_lower.startswith(prefix + "("):
            # feat(scope): message -> message
            match = re.match(r"^\w+\([^)]*\):\s*", subject, re.IGNORECASE)
            if match:
                return subject[match.end() :].strip() or subject
    return subject


def commits_to_entries(commits: Iterator) -> list[CommitEntry]:
    """Convert GitPython commit objects to CommitEntry list."""
    entries = []
    for commit in commits:
        message = commit.message or ""
        first_line = message.split("\n")[0] if message else "(no message)"
        category = _categorize(first_line)
        subject = _subject_display(first_line, category)
        date = commit.committed_datetime.strftime("%Y-%m-%d") if commit.committed_datetime else ""
        short_hash = commit.hexsha[:7] if commit.hexsha else ""
        entries.append(
            CommitEntry(
                short_hash=short_hash,
                date=date,
                subject=subject,
                category=category,
            )
        )
    return entries


def render_markdown(entries: list[CommitEntry]) -> str:
    """Render changelog entries as a single Markdown string."""
    by_category = {}
    for e in entries:
        by_category.setdefault(e.category, []).append(e)

    lines = ["# Changelog", ""]
    for cat in CATEGORY_ORDER:
        if cat not in by_category:
            continue
        lines.append(f"## {cat}")
        lines.append("")
        for e in by_category[cat]:
            lines.append(f"- {e.subject} (`{e.short_hash}`, {e.date})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
