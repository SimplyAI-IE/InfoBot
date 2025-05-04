This module powers the Concierge Experience for InfoBot. It uses deterministic logic, OCR, and fallback GPT reasoning — grounded in local data — to respond to guest queries.

🔧 Features
🧠 Intent Detection via GPT (strict fallback after classification)

📜 Static Knowledge Base using YAML (concierge_knowledge.yaml)

📅 Event Feed from Facebook via RSS (cached locally)

🖼️ Menu Parsing with OCR from readImages/ folder

🧭 Context-Aware GPT (only used when structured logic fails)

🚀 App Startup Flow
When the concierge app initializes:

facebook_feed.py pulls and caches local events

All images in readImages/ are scanned with OCR

OCR results are cached in ocr_cache/

YAML-based knowledge and intent flows are preloaded

📁 Key Files

File	Purpose
concierge_api.py	Main FastAPI entrypoint and router
startup.py	Triggers cache building on boot
facebook_feed.py	Loads and stores RSS events
ocr_cache.py	Extracts and caches text from images
concierge_gpt.py	GPT fallback engine (grounded only)
intent_gpt.py	Lightweight GPT intent classifier
concierge_knowledge.yaml	Local facts and answers
concierge_flow.yaml	Intent-specific follow-up prompts
gpt_engine.py	(To be deprecated: migrate logic to concierge_gpt.py)
🧪 Development Standards
✅ Ruff — Linting
Run auto-formatting and lint checks:

bash
Copy
Edit
ruff check . --fix
✅ Mypy — Type Checking
Ensure all code has valid type hints:

bash
Copy
Edit
mypy .
✅ Pre-Commit Hooks
To automate checks before every commit:

Install:

bash
Copy
Edit
pip install pre-commit
Add .pre-commit-config.yaml with Ruff + Mypy

Initialize:

bash
Copy
Edit
pre-commit install