from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Clock-in stats
    total_study_days = Column(Integer, default=0)
    consecutive_study_days = Column(Integer, default=0)
    last_study_date = Column(DateTime, nullable=True)

    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    total_episodes = Column(Integer)
    completed_episodes = Column(Integer, default=0)
    start_date = Column(DateTime, nullable=True)
    estimated_end_date = Column(DateTime, nullable=True)
    url = Column(String, nullable=True)
    color = Column(String, default='#409EFF')
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tasks")
