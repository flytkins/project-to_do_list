from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime   # ← добавили импорт

from .database import engine, SessionLocal
from .models import Base, Task

app = FastAPI(title="TODO API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# создаём таблицы
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "Backlog"

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime      # ← ИСПРАВЛЕНО: datetime, а не str

    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"message": "TODO API is running 🚀"}

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} deleted"}