from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db, get_session
from .models import Task
from .crud import create_task, get_tasks, get_task, update_task, delete_task
from .ai_utils import summarize_text, predict_priority
from pydantic import BaseModel
import asyncio

app = FastAPI(title="Kamba TODO API - FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Simple endpoints
class TaskIn(BaseModel):
    title: str
    description: str = ""

@app.post("/tasks", response_model=dict)
def api_create_task(payload: TaskIn):
    t = Task(title=payload.title, description=payload.description)
    # AI processing: summary + priority
    t.summary = summarize_text(payload.description or payload.title)
    t.priority = predict_priority(payload.title + " " + (payload.description or ""))
    created = create_task(t)
    # notify websockets (simple pubsub via global)
    NOTIFY_QUEUE.put_nowait({"action":"created","task_id":created.id})
    return created.dict()

@app.get("/tasks")
def api_get_tasks():
    return [t.dict() for t in get_tasks()]

@app.get("/tasks/{task_id}")
def api_get_task(task_id: int):
    t = get_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    return t.dict()

@app.put("/tasks/{task_id}")
def api_update_task(task_id: int, payload: dict):
    t = update_task(task_id, payload)
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    NOTIFY_QUEUE.put_nowait({"action":"updated","task_id":t.id})
    return t.dict()

@app.delete("/tasks/{task_id}")
def api_delete_task(task_id: int):
    t = delete_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    NOTIFY_QUEUE.put_nowait({"action":"deleted","task_id":task_id})
    return {"ok": True}

# Simple in-memory notify queue + websocket manager
NOTIFY_QUEUE = asyncio.Queue()

class ConnectionManager:
    def __init__(self):
        self.active = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict):
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws)

manager = ConnectionManager()

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # send recent tasks once
        await websocket.send_json({"action":"init", "tasks": [t.dict() for t in get_tasks()]})
        while True:
            msg = await NOTIFY_QUEUE.get()
            await manager.broadcast(msg)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
