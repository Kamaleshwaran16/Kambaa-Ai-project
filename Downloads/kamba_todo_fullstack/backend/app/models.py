from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = ""
    completed: bool = False
    priority: Optional[str] = "Medium"  # Low/Medium/High
    summary: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
