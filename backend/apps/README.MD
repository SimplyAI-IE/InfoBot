# 🧩 Apps Directory

This folder contains modular applications that plug into the InfoBot backend.

Each app is self-contained and follows the **deterministic-first** architecture of InfoBot:
- Structure flows using YAML
- Extract data using strict parsers
- Fallback to GPT only with injected, grounded context

---

## 📁 Sub-Apps

| Folder | Purpose |
|--------|---------|
| `concierge/` | Front-of-house interface for hotel guests — powered by intent resolution, Facebook events, OCR menus, and GPT fallback |
| `pension_guru/` | (Planned) Logic for structured pension calculations, based on fixed rules and YAML-controlled dialogue |
| `base_app.py` | Optional base class for shared app initialization and extension logic |

---

## 🧱 App Structure Standards

Each app may include:

| File | Purpose |
|------|---------|
| `*_api.py` | API router definition (mounted in `main.py`) |
| `*_flow.yaml` | Step-by-step conversation logic |
| `*_knowledge.yaml` | Static knowledge base used in replies |
| `*_gpt.py` | Fallback GPT module (must inject context only) |
| `*_startup.py` | Optional pre-load or validation logic |

---

## 🔌 How Apps Integrate

Apps are auto-mounted or registered via `main.py`. They must expose a router like:

```python
router = APIRouter()
@router.get("/some-endpoint") ...