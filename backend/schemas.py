from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    total_episodes: int
    completed_episodes: int = 0
    start_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None
    url: Optional[str] = None
    color: Optional[str] = "#409EFF"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    total_episodes: Optional[int] = None
    completed_episodes: Optional[int] = None
    start_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None
    url: Optional[str] = None
    color: Optional[str] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool = False
    total_study_days: int = 0
    consecutive_study_days: int = 0
    last_study_date: Optional[datetime] = None
    tasks: List[Task] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
