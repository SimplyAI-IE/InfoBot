# 🤖 InfoBot Backend

Handles structured planning, deterministic flows, and LLM fallback. Designed for environments needing precision and transparency.

---

## 🔍 Flow Hierarchy

Intent → Static (YAML / OCR / Feeds) → GPT (fallback only)

yaml
Copy
Edit

---

## 🔧 Key Modules

| Folder        | Purpose                                       |
|---------------|-----------------------------------------------|
| `apps/`       | Self-contained domain-specific logic          |
| `intents/`    | GPT-based intent classification               |
| `cache/`      | OCR results, scraped feeds, etc.              |
| `public/`     | Static fallback UI (legacy)                   |

---

## 🔌 Running the API

```bash
uvicorn main:app --reload
Expose endpoints such as:

/respond — Core API handler

/callback — Triggers WhatsApp escalation

yaml
Copy
Edit
