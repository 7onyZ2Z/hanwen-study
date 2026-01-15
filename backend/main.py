from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import crud, models, schemas, auth, database
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 初始化 Admin 用户
@app.on_event("startup")
def init_data():
    db = database.SessionLocal()
    try:
        user = crud.get_user_by_username(db, username="admin")
        if not user:
            print("Creating admin user...")
            admin_data = schemas.UserCreate(username="admin", password="123456") # 123456
            crud.create_user(db, admin_data, is_admin=True)
    finally:
        db.close()

# 允许跨域请求 (为了 Frontend)
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/users/clockin", response_model=schemas.User)
def clock_in_user(db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.clock_in(db, user_id=current_user.id)

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_user_task(db=db, task=task, user_id=current_user.id)

@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit, user_id=current_user.id)
    return tasks

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_task = crud.update_task(db, task_id=task_id, task_update=task_update, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    success = crud.delete_task(db, task_id=task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}

# --- Admin Endpoints ---

def get_current_admin_user(current_user: schemas.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@app.get("/admin/users", response_model=List[schemas.User])
def admin_get_users(skip: int = 0, limit: int = 100, db: Session = Depends(auth.get_db), admin: schemas.User = Depends(get_current_admin_user)):
    return crud.get_all_users(db, skip=skip, limit=limit)

@app.get("/admin/users/{user_id}/tasks", response_model=List[schemas.Task])
def admin_get_user_tasks(user_id: int, db: Session = Depends(auth.get_db), admin: schemas.User = Depends(get_current_admin_user)):
    return crud.get_tasks(db, user_id=user_id)

@app.put("/admin/tasks/{task_id}", response_model=schemas.Task)
def admin_update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(auth.get_db), admin: schemas.User = Depends(get_current_admin_user)):
    # Pass user_id=None to indicate admin override
    db_task = crud.update_task(db, task_id=task_id, task_update=task_update, user_id=None)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

