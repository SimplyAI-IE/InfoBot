# 🏨 Concierge App

This module powers the Concierge Experience for InfoBot. Responds to hotel guests with grounded answers based on:

- YAML knowledge base
- Facebook event feed (RSS)
- OCR-scanned menus
- Optional GPT fallback

---

## 🧭 App Features

- Intent Detection (`intent_gpt.py`)
- Static Knowledge (`concierge_knowledge.yaml`)
- Event Feed (`facebook_feed.py`)
- OCR Menus (`ocr_cache.py`)
- Web Scraping (`whitesands_scraper.py`)
- Escalation → WhatsApp Callback via `Messenger`

---

## 🚀 App Startup

```bash
uvicorn concierge_api:app --reload