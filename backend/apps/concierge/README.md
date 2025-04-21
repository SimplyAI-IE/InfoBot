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
