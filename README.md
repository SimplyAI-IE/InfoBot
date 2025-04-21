# InfoBot

A structured, GPT-powered retirement assistant focused on delivering precise, accurate State Pension and concierge services for users in the UK and Ireland.

## Features

- UK/IE State Pension estimator
- YAML-driven assistant flow
- GPT fallback with location-aware prompts
- Concierge system with image OCR + Facebook feed
- SQLite + SQLAlchemy persistence
- PDF export of results

## Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: Vanilla JS, HTML/CSS
- **Auth**: Google Sign-In (OAuth2)
- **Data**: SQLite + SQLAlchemy
- **AI**: OpenAI GPT-4
- **Hosting**: Render.com

## Structure

```
InfoBot/
├── backend/           # FastAPI backend
├── frontend/          # Static web frontend
├── public/            # HTML, JS, CSS
├── cache/             # Cached Facebook posts, etc.
├── tests/             # Test suite
```

## Quickstart

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Then visit: [http://localhost:8000/docs](http://localhost:8000/docs)