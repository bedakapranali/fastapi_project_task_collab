
from datetime import date, datetime
from pydantic import BaseModel
import uuid
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: Optional[str] = "medium"   # low, medium, high
    due_date: Optional[date] = None
    assigned_to: Optional[uuid.UUID] = None  # can assign later OR at creation


class TaskResponse(BaseModel):
    uid: uuid.UUID
    title: str
    description: str
    status: str
    priority: str
    due_date: Optional[date]
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TaskListResponse(BaseModel):
    total: int
    page : int
    limit: int
    tasks: list[TaskResponse]
#class TaskListResponse(BaseModel):



class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None        # pending, in_progress, completed
    priority: Optional[str] = None      # low, medium, high
    due_date: Optional[datetime] = None
    assigned_to: Optional[uuid.UUID] = None


