# Backend - Kamba TODO (FastAPI)

## Setup (local)
1. Create virtualenv: `python -m venv .venv && source .venv/bin/activate`
2. Install: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --reload --port 8000`

## Notes
- Uses SQLite (file: `db.sqlite`)
- AI features are in `app/ai_utils.py` and are optional. By default it uses sentence-transformers if installed.
- WebSocket endpoint provided for real-time updates.
