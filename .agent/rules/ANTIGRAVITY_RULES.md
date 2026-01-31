---
trigger: always_on
---

# Antigravity Rules & Project Standards

## Code Style (Python)
-   **Strict Minimization**: Remove unused imports, variables, and arguments immediately. Do not leave "dead code" commented out.
-   **Pydantic over Dataclasses**: Use `pydantic.BaseModel` for all data structures that cross module boundaries (API responses, Configs, Audit Results). Avoid `dataclasses` unless strictly internal and performance-critical.
-   **Type Hints Everywhere**: Use strict `mypy` standards. Every function argument and return must be typed. Use `Optional` and `Union` explicitly; never implicit `None`.
-   **Async First**: Use `asyncio` and `httpx` for I/O. Never block the event loop (e.g., no `time.sleep` or synchronous `requests`).
-   **Top-Level Imports**: Imports must be at the top. Group: Standard Lib -> Third Party -> Local. Remove unused imports instantly.
-   **Path Handling**: Use `pathlib.Path` over `os.path`.
-   **Config Management**: Use `pydantic-settings` to load from env vars. No hardcoded constants.
-   **Docstrings**: Google-style docstrings for all Modules, Classes, and Public Functions.

## Code Style (Frontend/React)
-   **Component Minimization**: Remove unused props and state. Inspect `lucide-react` imports to ensure only used icons are imported.
-   **Tailwind First**: Use utility classes for styling. Avoid custom CSS unless for complex animations.
-   **Clean Imports**: Remove unused hooks and libraries (e.g., `recharts`) if the feature is removed.

## Documentation
-   Keep specific specs in `docs/*.md`.
-   Update `docs/ROADMAP.md` as features are completed.
