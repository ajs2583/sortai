"""Git repository access using GitPython."""

from __future__ import annotations

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError


class GitError(Exception):
    """Raised when a git operation fails."""

    pass


def get_repo(path: str = ".") -> Repo:
    """Open the git repository at path (default: current directory).

    Raises GitError if path is not a valid git repository.
    """
    try:
        return Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise GitError(f"Not a git repository (or any parent): {path}")
    except Exception as e:
        raise GitError(f"Failed to open git repository: {e}") from e


def iter_commits(repo: Repo, since_tag: str | None = None):
    """Yield commit objects from the repo.

    If since_tag is set, only yield commits reachable from HEAD but not from
    that tag (i.e. commits "after" the tag). The tag must exist.
    """
    if since_tag is None:
        yield from repo.iter_commits()
        return

    try:
        # Rev spec "tag..HEAD" = commits reachable from HEAD but not from tag
        rev = f"{since_tag}..HEAD"
        yield from repo.iter_commits(rev)
    except (GitCommandError, ValueError) as e:
        raise GitError(f"Invalid or missing tag '{since_tag}': {e}") from e
