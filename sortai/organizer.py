"""Dry-run display, confirmation prompt, and file move execution."""

import os
import shutil
from pathlib import Path
from typing import Callable


def dry_run(root: Path, moves: list[tuple[str, str]], echo: Callable[[str], None]) -> None:
    """Print what would be moved where. No filesystem changes."""
    root = root.resolve()
    echo("Dry run – would move:")
    for rel_path, target_folder in moves:
        if target_folder == ".":
            dest_desc = "(keep at root)"
        else:
            dest_desc = f"{target_folder}/"
        echo(f"  {rel_path}  ->  {dest_desc}")


def confirm(echo: Callable[[str], None]) -> bool:
    """Prompt 'Apply these moves? [y/N]'. Returns True for y/yes, False otherwise."""
    try:
        answer = input("Apply these moves? [y/N] ").strip().lower()
    except EOFError:
        return False
    return answer in ("y", "yes")


def apply_moves(root: Path, moves: list[tuple[str, str]], echo: Callable[[str], None]) -> None:
    """
    Create target dirs and move files. Skips and warns if destination file already exists
    (no overwrite without user consent).
    """
    root = root.resolve()
    for rel_path, target_folder in moves:
        src = root / rel_path.replace("/", os.sep)
        if not src.is_file():
            echo(f"  Skip (not a file): {rel_path}")
            continue
        if target_folder == ".":
            continue
        target_dir = root / target_folder.replace("/", os.sep)
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / src.name
        if dest.exists() and dest.resolve() != src.resolve():
            echo(f"  Skip (destination exists): {rel_path} -> {dest.relative_to(root)}")
            continue
        try:
            shutil.move(str(src), str(dest))
            echo(f"  Moved: {rel_path} -> {target_folder}/")
        except OSError as e:
            echo(f"  Error moving {rel_path}: {e}")
