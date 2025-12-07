# Kamba TODO - Full Stack (FastAPI + React)

This repository contains a complete todo application:
- Backend: FastAPI + SQLite (with optional AI features)
- Frontend: React + Vite
- Real-time updates via WebSocket
- AI: Task summarizer + priority predictor (optional local model)

## Quick local run (recommended)
1. Backend:
   - cd backend
   - python -m venv .venv && source .venv/bin/activate
   - pip install -r requirements.txt
   - uvicorn app.main:app --reload --port 8000
2. Frontend:
   - cd frontend
   - npm install
   - npm run dev
3. Open http://localhost:5173

## Deploy
- Frontend: Vercel (connect frontend folder as a project, build command `npm run build`, publish `dist`)
- Backend: Render  (use Dockerfile or run with Uvicorn)

## Notes about AI features
- To enable stronger local AI (sentence-transformers), install `sentence-transformers` + `torch`.
- If heavy models are not installed, the app falls back to keyword heuristics for priority and a simple summarizer.
