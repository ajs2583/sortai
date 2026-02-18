# sortai

LLM-powered directory organizer. Uses **Google Gemini** to suggest a folder structure from filenames and (for text-based files) the first ~500 characters of content, then moves files into the suggested subfolders.

- **Dry-run by default** – see exactly what would move where before touching anything.
- **Confirm before apply** – with `--apply`, you are prompted to confirm before any files are moved.

📦 **PyPI Package:** [https://pypi.org/project/sortai/0.1.0/](https://pypi.org/project/sortai/0.1.2/)

## Install

Install from PyPI:

```bash
pip install sortai
```

Or view the package on [PyPI](https://pypi.org/project/sortai/0.1.0/).

Development install from source:

```bash
git clone https://github.com/ajs2583/sortai.git
cd sortai
pip install -e .
```

## Setup

Set your Google Gemini API key (required):

```bash
export GEMINI_API_KEY=your_key_here
```

Get a key at: **https://aistudio.google.com/app/apikey**

You can copy `.env.example` to `.env` and set `GEMINI_API_KEY` there; load it with your shell or a tool like `python-dotenv` if you use one (sortai does not load `.env` automatically).

## Demo

![Demo](https://raw.githubusercontent.com/ajs2583/sortai/main/docs/demo.gif)

*Demo showing `sortai test-demo` dry-run preview, then `--apply` with confirmation.*

## Usage

| Command | Description |
|--------|-------------|
| `sortai <path>` | Dry-run: show what would be moved where (default). |
| `sortai <path> --apply` | After dry-run, prompt and then actually move files. |
| `sortai <path> --depth 2` | Organize up to 2 levels of subfolders (e.g. `documents/work`). |
| `sortai <path> --model gemini-2.5-flash` | Override Gemini model (default: gemini-2.5-flash). |
| `sortai --version` | Print version. |
| `sortai --help` | Show help. |

### Example output

**Before (flat directory):**

```
my-folder/
├── report.pdf
├── notes.txt
├── budget.csv
├── vacation.jpg
└── readme.md
```

**Dry-run:**

```
$ sortai ./my-folder
Dry run – would move:
  report.pdf  ->  documents/
  notes.txt   ->  documents/
  budget.csv  ->  finance/
  vacation.jpg ->  images/
  readme.md   ->  (keep at root)
Run with --apply to perform moves.
```

**After applying:**

```
my-folder/
├── readme.md
├── documents/
│   ├── report.pdf
│   └── notes.txt
├── finance/
│   └── budget.csv
└── images/
    └── vacation.jpg
```

## Supported file types for content reading

sortai reads the **first ~500 characters** of content for:

- `.pdf` (first page via pdfplumber)
- `.txt`, `.md`, `.csv` (plain text)
- `.docx` (paragraph text via python-docx)

All other files are categorized by **filename and extension only**.

## Releasing

### GitHub Releases (Automated)

1. **Bump version** in `pyproject.toml` and `sortai/__init__.py` (e.g., `0.1.0` → `0.1.1`).

2. **Commit and push**:
   ```bash
   git add pyproject.toml sortai/__init__.py
   git commit -m "Bump version to 0.1.1"
   git push
   ```

3. **Create and push a tag**:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

4. **GitHub Actions will automatically**:
   - Verify version consistency
   - Build the package (wheel + sdist)
   - Create a GitHub release with release notes
   - Attach the built artifacts

The workflow triggers on tags matching `v*.*.*` (e.g., `v0.1.0`). You can also trigger it manually from the Actions tab.

### Publishing to PyPI

1. **Create a PyPI account** (and optionally [Test PyPI](https://test.pypi.org/) for testing):
   - https://pypi.org/account/register/

2. **Install build tools** (one-time):
   ```bash
   pip install build twine
   ```

3. **Bump version** in `pyproject.toml` and `sortai/__init__.py` when releasing a new version.

4. **Build the package** (from the project root):
   ```bash
   python -m build
   ```
   This creates `dist/sortai-0.1.0.tar.gz` and a wheel.

5. **Upload to PyPI** (manual):
   ```bash
   twine upload dist/*
   ```
   Twine will prompt for your PyPI username and password. Prefer an [API token](https://pypi.org/manage/account/token/) (username: `__token__`, password: your token) over your account password.

   **Or enable automated PyPI upload**: Add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`, then edit `.github/workflows/release.yml` and change `if: false` to `if: true` in the "Upload to PyPI" step. Releases will then automatically publish to PyPI.

   To try Test PyPI first:
   ```bash
   twine upload --repository testpypi dist/*
   ```
   Then install with: `pip install -i https://test.pypi.org/simple/ sortai`

**Note:** If the name `sortai` is already taken on PyPI, change the `name` in `pyproject.toml` to something unique (e.g. `sortai-cli`) and publish under that name.

## License

MIT


