"""Click CLI entrypoint for sortai."""

import os
from pathlib import Path

import click

from sortai import __version__
from sortai.ai import GEMINI_API_KEY_URL, MissingApiKeyError, get_moves
from sortai.organizer import apply_moves, confirm, dry_run
from sortai.reader import list_files


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=False,
    default=None,
)
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help="Actually move files after confirmation (default: dry-run only).",
)
@click.option(
    "--depth",
    type=int,
    default=1,
    help="Organize recursively up to N levels of subfolders (default: 1).",
)
@click.option(
    "--model",
    type=str,
    default="gemini-1.5-flash",
    help="Gemini model name (default: gemini-1.5-flash).",
)
@click.option(
    "--version",
    "show_version",
    is_flag=True,
    default=False,
    help="Show version and exit.",
)
def main(
    path: Path | None,
    apply: bool,
    depth: int,
    model: str,
    show_version: bool,
) -> None:
    """Organize files in a directory using Google Gemini."""
    if show_version:
        click.echo(f"sortai {__version__}")
        raise SystemExit(0)

    if path is None:
        click.echo("Error: PATH is required. Use --help for usage.", err=True)
        raise SystemExit(1)

    root = path.resolve()
    if not root.is_dir():
        click.echo(f"Error: not a directory: {path}", err=True)
        raise SystemExit(1)

    if not (os.environ.get("GEMINI_API_KEY") or "").strip():
        click.echo("Error: GEMINI_API_KEY is not set.", err=True)
        click.echo(f"Get an API key at: {GEMINI_API_KEY_URL}", err=True)
        raise SystemExit(1)

    file_list = list_files(root, max_depth=depth)
    if not file_list:
        click.echo("No files found to organize.")
        raise SystemExit(0)

    try:
        moves = get_moves(file_list, depth=depth, model_name=model)
    except MissingApiKeyError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo(f"Get an API key at: {GEMINI_API_KEY_URL}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error calling Gemini: {e}", err=True)
        raise SystemExit(1)

    if not moves:
        click.echo("No moves suggested.")
        raise SystemExit(0)

    dry_run(root, moves, echo=click.echo)
    if not apply:
        click.echo("Run with --apply to perform moves.")
        raise SystemExit(0)

    if not confirm(echo=click.echo):
        click.echo("Aborted.")
        raise SystemExit(0)

    apply_moves(root, moves, echo=click.echo)
    click.echo("Done.")


if __name__ == "__main__":
    main()
