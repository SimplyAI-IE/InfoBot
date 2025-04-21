# Concierge App

This module powers the concierge experience for InfoBot.

## Features

- GPT-based intent detection
- Static YAML + JSON knowledge resolution
- Facebook RSS feed integration
- OCR pipeline for extracting menu items from images
- GPT fallback with location-specific grounding

## Startup

On app startup:
- Facebook RSS is pulled and cached
- `readImages/` is scanned
- OCR text is extracted and cached in `ocr_cache/`

## Files

- `concierge_api.py` — main FastAPI route and flow logic
- `ocr_cache.py` — handles OCR extraction and caching
- `facebook_feed.py` — pulls and caches Facebook RSS
- `startup.py` — concierge-only startup logic
- `concierge_gpt.py` — GPT-based intent + response handling
- `concierge_knowledge.yaml` — static hotel facts
- `concierge_flow.yaml` — controls follow-up prompts per intent


Development Standards
To maintain code quality, all contributions must pass the following checks:

✅ Code Style — Ruff
We use Ruff for linting and auto-formatting. It ensures compliance with PEP8 and flags common issues such as:

Unused imports

Bad indentation

Naming violations

Complexity thresholds

Run manually:

bash
Copy
Edit
ruff check . --fix
✅ Static Typing — Mypy
All Python code must include type hints. We use Mypy for static type checking.

Run manually:

bash
Copy
Edit
mypy .
✅ Pre-Commit Hook
To enforce these checks automatically before each commit, install pre-commit:

Install dependencies:

bash
Copy
Edit
pip install pre-commit
Add this config to .pre-commit-config.yaml:

yaml
Copy
Edit
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.4.2
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
Enable it in your repo:

bash
Copy
Edit
pre-commit install