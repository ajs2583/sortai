"""CLI entry point for Logcraft."""

from __future__ import annotations

import click

from logcraft import __version__
from logcraft.changelog import commits_to_entries, render_markdown
from logcraft.git_utils import GitError, get_repo, iter_commits


def main() -> None:
    """Run the Logcraft CLI (entry point for console script)."""
    cli()


@click.command()
@click.option(
    "--since",
    default=None,
    metavar="TAG",
    help="Only include commits since this tag (e.g. --since v1.0.0).",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    default="CHANGELOG.md",
    metavar="FILE",
    help="Output file path (default: CHANGELOG.md).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print changelog to terminal instead of writing a file.",
)
@click.option(
    "--version",
    "show_version",
    is_flag=True,
    help="Show version and exit.",
)
def cli(
    since: str | None,
    output_path: str,
    dry_run: bool,
    show_version: bool,
) -> None:
    """Craft CHANGELOG.md from git commit history.

    Run from a git repository root. Commits are categorized by conventional
    prefixes: feat: -> Features, fix: -> Bug Fixes, chore: -> Maintenance.
    """
    if show_version:
        click.echo(f"Logcraft {__version__}")
        return

    try:
        repo = get_repo(".")
    except GitError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1) from e

    try:
        commits = list(iter_commits(repo, since_tag=since))
    except GitError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1) from e

    entries = commits_to_entries(commits)
    markdown = render_markdown(entries)

    if dry_run:
        click.echo(markdown)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        click.echo(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
