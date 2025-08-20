from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

app = FastAPI(title="Sistema de Gestión de Tareas - Semana 1")

# =============================
# MODELOS Pydantic
# =============================

class Preferences(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "es"
    timezone: Optional[str] = "UTC"

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    preferences: Preferences

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str]
    preferences: Optional[Preferences] = Preferences()

class Category(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    user_id: int

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str]
    color: Optional[str]

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$")
    status: str = Field(..., pattern="^(pending|in_progress|completed|cancelled)$")
    category_id: int
    user_id: int
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []

class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    priority: str
    status: str
    category_id: int
    user_id: int
    due_date: Optional[date]
    tags: List[str] = []

# =============================
# BASE DE DATOS EN MEMORIA
# =============================

fake_users = []
fake_categories = []
fake_tasks = []

# =============================
# ENDPOINTS USERS
# =============================

@app.post("/users", response_model=User)
def create_user(user: UserCreate):
    new_id = len(fake_users) + 1
    new_user = User(
        id=new_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        created_at=datetime.now(),
        preferences=user.preferences or Preferences()
    )
    fake_users.append(new_user)
    return new_user

@app.get("/users/me", response_model=User)
def get_me():
    if not fake_users:
        raise HTTPException(status_code=404, detail="No hay usuarios registrados")
    return fake_users[0]

@app.put("/users/me", response_model=User)
def update_me(user: UserCreate):
    if not fake_users:
        raise HTTPException(status_code=404, detail="No hay usuarios registrados")
    current_user = fake_users[0]
    current_user.username = user.username
    current_user.email = user.email
    current_user.full_name = user.full_name
    current_user.preferences = user.preferences
    return current_user

@app.delete("/users/me")
def delete_me():
    if not fake_users:
        raise HTTPException(status_code=404, detail="No hay usuarios registrados")
    fake_users.clear()
    return {"message": "Cuenta eliminada"}

# =============================
# ENDPOINTS CATEGORIES
# =============================

@app.post("/categories", response_model=Category)
def create_category(cat: CategoryCreate):
    if not fake_users:
        raise HTTPException(status_code=400, detail="Debe existir un usuario primero")
    new_id = len(fake_categories) + 1
    new_category = Category(
        id=new_id,
        name=cat.name,
        description=cat.description,
        color=cat.color,
        user_id=fake_users[0].id
    )
    fake_categories.append(new_category)
    return new_category

@app.get("/categories", response_model=List[Category])
def list_categories():
    return fake_categories

@app.put("/categories/{category_id}", response_model=Category)
def update_category(category_id: int, cat: CategoryCreate):
    category = next((c for c in fake_categories if c.id == category_id), None)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    category.name = cat.name
    category.description = cat.description
    category.color = cat.color
    return category

@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    global fake_categories
    fake_categories = [c for c in fake_categories if c.id != category_id]
    return {"message": "Categoría eliminada"}

# =============================
# ENDPOINTS TASKS
# =============================

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    if not fake_users:
        raise HTTPException(status_code=400, detail="Debe existir un usuario primero")
    new_id = len(fake_tasks) + 1
    new_task = Task(
        id=new_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        category_id=task.category_id,
        user_id=task.user_id,
        due_date=task.due_date,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tags=task.tags
    )
    fake_tasks.append(new_task)
    return new_task

@app.get("/tasks", response_model=List[Task])
def list_tasks(status: Optional[str] = None, priority: Optional[str] = None):
    tasks = fake_tasks
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = next((t for t in fake_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate):
    current_task = next((t for t in fake_tasks if t.id == task_id), None)
    if not current_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    current_task.title = task.title
    current_task.description = task.description
    current_task.priority = task.priority
    current_task.status = task.status
    current_task.category_id = task.category_id
    current_task.user_id = task.user_id
    current_task.due_date = task.due_date
    current_task.updated_at = datetime.now()
    current_task.tags = task.tags
    return current_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global fake_tasks
    fake_tasks = [t for t in fake_tasks if t.id != task_id]
    return {"message": "Tarea eliminada"}

@app.patch("/tasks/{task_id}/status", response_model=Task)
def change_status(task_id: int, status: str = Query(..., pattern="^(pending|in_progress|completed|cancelled)$")):
    task = next((t for t in fake_tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    task.status = status
    task.updated_at = datetime.now()
    return task

# =============================
# ENDPOINTS STATS
# =============================

@app.get("/stats/summary")
def stats_summary():
    total = len(fake_tasks)
    by_status = {s: len([t for t in fake_tasks if t.status == s]) for s in ["pending", "in_progress", "completed", "cancelled"]}
    overdue = len([t for t in fake_tasks if t.due_date and t.due_date < date.today()])
    return {"total_tasks": total, "by_status": by_status, "overdue_tasks": overdue}

@app.get("/stats/productivity")
def stats_productivity():
    completed = len([t for t in fake_tasks if t.status == "completed"])
    return {"completed_tasks": completed, "week_productivity": f"{(completed/len(fake_tasks)*100) if fake_tasks else 0:.2f}%"}

