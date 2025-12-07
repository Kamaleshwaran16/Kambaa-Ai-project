from sqlmodel import select
from .models import Task
from .db import get_session

def create_task(task: Task):
    with get_session() as s:
        s.add(task)
        s.commit()
        s.refresh(task)
        return task

def get_tasks():
    with get_session() as s:
        return s.exec(select(Task).order_by(Task.created_at.desc())).all()

def get_task(task_id: int):
    with get_session() as s:
        return s.get(Task, task_id)

def update_task(task_id: int, data: dict):
    with get_session() as s:
        t = s.get(Task, task_id)
        if not t: 
            return None
        for k,v in data.items():
            setattr(t, k, v)
        s.add(t); s.commit(); s.refresh(t)
        return t

def delete_task(task_id: int):
    with get_session() as s:
        t = s.get(Task, task_id)
        if t:
            s.delete(t); s.commit()
        return t
