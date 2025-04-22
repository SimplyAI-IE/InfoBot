InfoBot
InfoBot is a deterministic assistant framework designed for environments where precision and traceability are paramount, such as retirement planning and concierge services. It leverages the strengths of large language models (LLMs) for interpretation and fallback, ensuring factual integrity is never compromised.​

🧠 Core Philosophy
"Use LLMs to fill gaps — not to make things up."​

InfoBot tightly controls flow using deterministic logic:​

All guided conversations are defined in conversation_flow.yaml.

All extracted data fields are verified and logged.

All projections are calculated using strict rules in pension_calculator.py.

GPT is only invoked when:

A fallback is needed.

A query is unstructured.

A known source of truth (e.g., OCR or RSS) is provided for context.​

🧱 Architecture Overview
Backend
Web Server: FastAPI (main.py) — async, modular.

Routing: Modular routers under apps/.

Memory: memory.py — in-memory for anonymous sessions, database for authenticated sessions.

Database: SQLite via SQLAlchemy ORM.

Auth: Google Sign-In (OAuth2).

AI: OpenAI GPT-4, used only after validation.

Flow Logic: conversation_flow.yaml + flow_engine.py.

Data Extraction: extract_user_data.py — strict, rule-based.

Calculation: pension_calculator.py — no AI used.​

OCR + Image Processing
Engine: Tesseract OCR via pytesseract.

Caching: Text stored in ocr_cache/.

Input Images: Placed in readImages/.

Context Use: Injected into GPT prompts when relevant.​

Live Content Ingestion
Source: Facebook.

Parser: RSS.app.

Caching: facebook_feed.py → YAML cache.​
GitHub
+1
Home
+1

Frontend
UI: HTML/CSS + Vanilla JS.

Chat Logic: chat.js handles message flow.

Auth: Google OAuth2 button.​

🧪 Testing
Framework: Pytest.

Coverage: OCR, concierge routing, fallback.

Mode: CLI + CI/CD ready.​

📄 Documentation & Traceability
README.md: Root project overview.

apps/concierge/README.md: Full breakdown of GPT + OCR.

ocr_cache/README.md: Describes text caching strategy.

facebook_feed.py: Pulls live event posts.​
Wikipedia

🧩 Vision for Extension
Plug-and-play apps (apps/) for new domains.

Structured caching of Facebook, image OCR, and public data.

Hybrid GPT + YAML routing for always-grounded conversations.

Optional user memory for follow-up flows, PDF summaries, and personalization.​

🔒 Design Constraints
GPT is never called until:

The user's intent is resolved.

All static knowledge bases fail to satisfy the query.

Prompts explicitly list:

What’s true.

What’s false.

What the bot must not say (e.g., “the hotel has a pool”).​

📌 Why This Matters
Every GPT response is explainable.

Outputs are grounded in verifiable data (OCR, YAML, RSS).

Risk of hallucination is tightly controlled.

Easy to test, debug, and extend.​

🚀 Getting Started
Clone the repository:

bash
Copy
Edit
git clone https://github.com/SimplyAI-IE/InfoBot.git
cd InfoBot
Set up a virtual environment:

bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the application:

bash
Copy
Edit
uvicorn backend.main:app --reload
🧰 Development Tools
Linting: Ruff.

Formatting: Black.

Type Checking: Mypy.

Pre-commit Hooks: Configured to run linting, formatting, and type checking on each commit.​

## Domain & Hosting

- **Domain Registrar**: [Blacknight](https://www.blacknight.com)
  - DNS access: [cp.blacknighthosting.com](https://cp.blacknighthosting.com)
- **Hosting Provider**: [A2 Hosting](https://www.a2hosting.com)
  - Hosting panel: **cPanel**
  - Files and site deployment: Managed via `public_html` directory

## Deployment Strategy

- Static builds (from Astro) should be uploaded to `public_html/test-ui` or a subdomain (e.g., `test.simplyai.ie`) for staging purposes.
- Production deployment will eventually overwrite the root site
