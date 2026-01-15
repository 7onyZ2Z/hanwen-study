from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_tasks(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    return db.query(models.Task).filter(models.Task.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate, user_id: int):
    # Base query
    query = db.query(models.Task).filter(models.Task.id == task_id)
    
    # If not admin (user_id is provided), ensure ownership
    if user_id is not None:
        query = query.filter(models.Task.owner_id == user_id)
        
    db_task = query.first()
    
    if db_task:
        update_data = task_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int):
    query = db.query(models.Task).filter(models.Task.id == task_id)
    if user_id is not None:
        query = query.filter(models.Task.owner_id == user_id)
        
    db_task = query.first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

# Deprecated or alias to update_task for compatibility if needed, but better to refactor usage
def update_task_progress(db: Session, task_id: int, completed_episodes: int, user_id: int):
    return update_task(db, task_id, schemas.TaskUpdate(completed_episodes=completed_episodes), user_id)


def clock_in(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return None
    
    from datetime import datetime, date, timedelta
    now = datetime.utcnow()
    today_date = now.date()
    
    # Check if already clocked in today
    if user.last_study_date and user.last_study_date.date() == today_date:
        return user # Already clocked in
        
    # Check if consecutive
    if user.last_study_date and user.last_study_date.date() == today_date - timedelta(days=1):
        user.consecutive_study_days += 1
    else:
        user.consecutive_study_days = 1
        
    user.total_study_days += 1
    user.last_study_date = now
    
    db.commit()
    db.refresh(user)
    return user
