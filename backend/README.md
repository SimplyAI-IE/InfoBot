# 🤖 InfoBot

InfoBot is a deterministic-first assistant framework for domains requiring traceability, structure, and verifiable logic — like retirement planning or concierge services.

---

## 🧠 Core Philosophy

- 💡 **Deterministic by Default** — YAML flows, rule-based logic
- 🔎 **Fallback to AI** — GPT is used *only* when structured responses fail
- 🔒 **Explainable Outputs** — All AI responses are grounded in real OCR, feeds, or YAML

---

## 🏗️ Project Structure

| Folder | Purpose |
|--------|---------|
| `backend/` | FastAPI server with all app logic |
| `frontend/` | Lightweight HTML/JS chat UI |
| `apps/` | Modular domain logic (e.g. concierge, pensions) |
| `ocr_cache/` | Cached OCR text from scanned images |
| `readImages/` | Input folder for signs, menus, etc. |
| `memory.db` | Persistent session DB (for logged-in users) |

---

## 🧩 Key Modules

- `conversation_flow.yaml` — Dialogue routing logic
- `pension_calculator.py` — Hard-coded pension rules
- `extract_user_data.py` — Maps freeform input to fields
- `concierge_gpt.py` — Context-injected GPT fallback only
- `intent_gpt.py` — Classifies user query as "wifi", "golf", etc.

---

## 🚀 Running the Project

```bash
pip install -r requirements.txt
python backend/init_db.py
uvicorn backend.main:app --reload
Open http://localhost:8000 to start chatting.

🔍 Developer Standards
✅ ruff check . --fix (formatting)

✅ mypy . (type checks)

✅ pytest (test coverage pending)

✅ GPT is disabled unless structured fallback triggers it

🔐 Auth & Memory
Anonymous users → in-memory only

Logged-in users → SQLite via memory.db

Google OAuth2 used for auth flow (if enabled)

📦 Deployment
Coming soon: render.yaml or Docker support