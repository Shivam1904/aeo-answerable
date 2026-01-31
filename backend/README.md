# AEO Answerable - Backend (Python)

The core execution engine for AEO Answerable, built with **FastAPI**, **Playwright**, and **BeautifulSoup**.

## Development Standards

### 1. Code Quality
-   **Pydantic First**: We use Pydantic `BaseModel` for all data schemas (Configs, API Responses, Audit Results). This ensures automatic validation and easy JSON serialization. Avoid `dataclasses`.
-   **Async I/O**: All network operations (crawling, retrieval) must be `async`. Use `httpx` and `asyncio`.
-   **Strict Typing**: All functions must have type hints.

### 2. Minimization
-   **No Dead Code**: Unused imports (e.g., `asyncio` when not used), unused function arguments, and commented-out blocks must be removed before committing.
-   **Lean Dependencies**: Only import what you need.

## Setup

```bash
# From project root
source ../venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Run the CLI scan
python -m aeo.cli scan https://example.com

# Run the API server
uvicorn aeo.api:app --reload
```

## Directory Structure
-   `api.py`: FastAPI application and endpoints.
-   `cli.py`: Typer-based CLI commands.
-   `crawler.py`: Async HTTP crawler (httpx).
-   `rendered_crawler.py`: Headless browser crawler (Playwright).
-   `auditor.py`: Content scoring logic.
-   `extractor.py`: HTML processing and cleaning.
