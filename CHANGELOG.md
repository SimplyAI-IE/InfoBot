## [v0.2.0] – 2025-04-21
### Added
- ✅ Full `mypy` type coverage across all 26 backend files
- ✅ `mypy.ini` with strict settings and optional enforcement
- ✅ BaseApp interface hardened with optional dict handling
- ✅ Explicit ChatCompletionMessageParam typing for OpenAI calls
- ✅ Logging routed to rotating file logs in `logs/error.log`
- ✅ GitHub Actions pipeline for `pytest`, `ruff`, `mypy`

### Fixed
- 🐛 Removed legacy imports of `save_user_profile`, `get_user_profile`
- 🔁 Switched from `openai.ChatCompletion.create()` to `client.chat.completions.create()`
- 🔧 Corrected use of `urljoin`, `urlparse`, `.strip()` on Optional values
- ✏️ Cleaned all invalid base class references in `models.py`

### Removed
- 🚫 Duplicate FastAPI route for `/concierge/facts`
- 🗃️ Legacy `extract_user_data` logic that violated type safety
