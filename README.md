# Logcraft

**Craft changelogs from git.** Logcraft turns your commit history into a formatted **CHANGELOG.md**, with commits automatically categorized by conventional commit prefixes.

## Install

```bash
pip install logcraft
```

## Usage

Run from the root of any git repository:

```bash
logcraft
```

This writes **CHANGELOG.md** in the current directory, grouping commits by category.

### Options

| Option | Description |
|--------|-------------|
| `--since TAG` | Only include commits since the given tag (e.g. `--since v1.0.0`). |
| `--output FILE`, `-o FILE` | Output file path (default: `CHANGELOG.md`). |
| `--dry-run` | Print the changelog to the terminal instead of writing a file. |
| `--version` | Show the tool version and exit. |

### Examples

```bash
# Generate CHANGELOG.md in the current directory
logcraft

# Changelog since a specific tag
logcraft --since v1.0.0

# Write to a custom file
logcraft --output HISTORY.md
logcraft -o docs/changelog.md

# Preview without writing
logcraft --dry-run

# Show version
logcraft --version
```

### Commit categories

Commit messages are categorized by the first-line prefix (case-insensitive):

| Prefix | Category |
|--------|----------|
| `feat:` | Features |
| `fix:` | Bug Fixes |
| `chore:` | Maintenance |
| (anything else) | Other |

Each changelog entry shows the commit subject, short hash, and date.

## Development

From the project root:

```bash
pip install -e .
logcraft --help
```

## Publishing to PyPI

1. **Create a PyPI account** and an [API token](https://pypi.org/manage/account/token/) (scope: entire account or just this project).

2. **Build the package:**
   ```bash
   pip install build twine
   python -m build
   ```

3. **Upload** (run in your terminal so you can enter credentials):
   ```bash
   twine upload dist/*
   ```
   When prompted:
   - **Username:** `__token__`
   - **Password:** your PyPI API token (starts with `pypi-`)

   Or use environment variables (no prompt):
   ```bash
   $env:TWINE_USERNAME = "__token__"
   $env:TWINE_PASSWORD = "pypi-your-api-token"
   twine upload dist/*
   ```

## License

MIT
