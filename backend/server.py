from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = "project_management_secret_key_2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# User Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "Team Member"  # Admin, Manager, Team Member

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Project Models
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = ""
    owner_id: str
    team_members: List[str] = Field(default_factory=list)  # List of user IDs who are team members
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Project Team Management Models
class ProjectTeamUpdate(BaseModel):
    team_members: List[str]

# Task Models  
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    project_id: str
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "To Do"  # To Do, In Progress, Done

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = ""
    project_id: str
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "To Do"
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Notification Models
class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    message: str
    type: str  # "task_assignment", "due_date", "status_change", "comment"
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str
    task_id: Optional[str] = None
    project_id: Optional[str] = None

# File Attachment Models
class FileAttachment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    filename: str
    content_type: str
    file_data: str  # base64 encoded file data
    file_size: int
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class FileUpload(BaseModel):
    task_id: str
    filename: str
    content_type: str
    file_data: str

# Comment Models
class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    user_id: str
    user_name: str
    content: str
    parent_id: Optional[str] = None  # For threaded comments
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class CommentCreate(BaseModel):
    task_id: str
    content: str
    parent_id: Optional[str] = None

class CommentUpdate(BaseModel):
    content: str

# Progress Analytics Models
class ProgressStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    todo_tasks: int
    completion_rate: float
    overdue_tasks: int

class ProjectProgress(BaseModel):
    project_id: str
    project_title: str
    stats: ProgressStats

# Auth helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return User(**user)

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user
    user_obj = User(name=user.name, email=user.email, role=user.role)
    user_dict = user_obj.dict()
    user_dict["password"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    user = await db.users.find_one({"email": user_login.email})
    if not user or not verify_password(user_login.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    user_obj = User(**user)
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# User Routes
@api_router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_user)):
    """Get all users for team management (authenticated users only)"""
    users = await db.users.find({}).to_list(1000)
    return [User(**user) for user in users]

# Project Routes
@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user)):
    project_obj = Project(
        title=project.title,
        description=project.description,
        owner_id=current_user.id,
        team_members=[]  # Initialize with empty team
    )
    await db.projects.insert_one(project_obj.dict())
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)):
    projects = await db.projects.find({"owner_id": current_user.id}).to_list(1000)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

@api_router.put("/projects/{project_id}/team", response_model=Project)
async def update_project_team(project_id: str, team_update: ProjectTeamUpdate, current_user: User = Depends(get_current_user)):
    """Add/remove team members from project (only project owner can do this)"""
    project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or you're not the owner")
    
    # Update team members
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"team_members": team_update.team_members}}
    )
    
    # Get updated project
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**updated_project)

@api_router.get("/projects/accessible", response_model=List[Project])
async def get_accessible_projects(current_user: User = Depends(get_current_user)):
    """Get projects user owns OR is a team member of"""
    projects = await db.projects.find({
        "$or": [
            {"owner_id": current_user.id},  # Projects user owns
            {"team_members": current_user.id}  # Projects user is a team member of
        ]
    }).to_list(1000)
    return [Project(**project) for project in projects]

# Task Routes
@api_router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    # Verify project exists and user has access
    project = await db.projects.find_one({"id": task.project_id, "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_obj = Task(
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        assigned_to=task.assigned_to,
        due_date=task.due_date,
        status=task.status,
        created_by=current_user.id
    )
    await db.tasks.insert_one(task_obj.dict())
    
    # Create notification if task is assigned to someone
    if task.assigned_to and task.assigned_to != current_user.id:
        assigned_user = await db.users.find_one({"id": task.assigned_to})
        if assigned_user:
            notification = Notification(
                user_id=task.assigned_to,
                title="Task Assigned",
                message=f"You have been assigned to task: {task.title}",
                type="task_assignment",
                task_id=task_obj.id,
                project_id=task.project_id
            )
            await db.notifications.insert_one(notification.dict())
    
    return task_obj

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(project_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    if project_id:
        # Verify project access (owner OR team member OR has assigned tasks)
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if user has access (owner, team member, or assigned tasks)
        has_access = (
            project["owner_id"] == current_user.id or  # Owner
            current_user.id in project.get("team_members", []) or  # Team member
            bool(await db.tasks.find_one({"project_id": project_id, "assigned_to": current_user.id}))  # Has assigned tasks
        )
        
        if not has_access:
            raise HTTPException(status_code=404, detail="Project not found")
        
        tasks = await db.tasks.find({"project_id": project_id}).to_list(1000)
    else:
        # Get all accessible projects
        accessible_projects = await db.projects.find({
            "$or": [
                {"owner_id": current_user.id},
                {"team_members": current_user.id}
            ]
        }).to_list(1000)
        project_ids = [p["id"] for p in accessible_projects]
        
        # Get tasks from accessible projects OR assigned to user
        tasks = await db.tasks.find({
            "$or": [
                {"project_id": {"$in": project_ids}},
                {"assigned_to": current_user.id}
            ]
        }).to_list(1000)
    
    return [Task(**task) for task in tasks]

@api_router.put("/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: dict, current_user: User = Depends(get_current_user)):
    # Find task and verify access
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify project access
    project = await db.projects.find_one({"id": task["project_id"], "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    old_status = task["status"]
    new_status = status["status"]
    
    # Update status
    await db.tasks.update_one({"id": task_id}, {"$set": {"status": new_status}})
    
    # Create notification for status change
    if old_status != new_status:
        # Notify task owner if different from user making the change
        if task["created_by"] != current_user.id:
            notification = Notification(
                user_id=task["created_by"],
                title="Task Status Updated",
                message=f"Task '{task['title']}' status changed from {old_status} to {new_status}",
                type="status_change",
                task_id=task_id,
                project_id=task["project_id"]
            )
            await db.notifications.insert_one(notification.dict())
        
        # Notify assigned user if different from both owner and user making the change
        if task.get("assigned_to") and task["assigned_to"] != current_user.id and task["assigned_to"] != task["created_by"]:
            notification = Notification(
                user_id=task["assigned_to"],
                title="Task Status Updated",
                message=f"Task '{task['title']}' status changed from {old_status} to {new_status}",
                type="status_change",
                task_id=task_id,
                project_id=task["project_id"]
            )
            await db.notifications.insert_one(notification.dict())
    
    # Get updated task
    updated_task = await db.tasks.find_one({"id": task_id})
    return Task(**updated_task)

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    # Find task and verify access
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify project access
    project = await db.projects.find_one({"id": task["project_id"], "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete task
    result = await db.tasks.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}

# Notification Routes
@api_router.post("/notifications", response_model=Notification)
async def create_notification(notification: NotificationCreate, current_user: User = Depends(get_current_user)):
    notification_obj = Notification(**notification.dict())
    await db.notifications.insert_one(notification_obj.dict())
    return notification_obj

@api_router.get("/notifications", response_model=List[Notification])
async def get_notifications(current_user: User = Depends(get_current_user)):
    notifications = await db.notifications.find({"user_id": current_user.id}).sort("created_at", -1).to_list(100)
    return [Notification(**notification) for notification in notifications]

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: User = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user.id},
        {"$set": {"read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@api_router.get("/notifications/unread-count")
async def get_unread_notification_count(current_user: User = Depends(get_current_user)):
    count = await db.notifications.count_documents({"user_id": current_user.id, "read": False})
    return {"count": count}

# File Attachment Routes
@api_router.post("/files", response_model=FileAttachment)
async def upload_file(file: FileUpload, current_user: User = Depends(get_current_user)):
    # Verify task exists and user has access
    task = await db.tasks.find_one({"id": file.task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = await db.projects.find_one({"id": task["project_id"], "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate file size from base64 data
    import base64
    try:
        decoded_data = base64.b64decode(file.file_data)
        file_size = len(decoded_data)
    except:
        raise HTTPException(status_code=400, detail="Invalid file data")
    
    # Check file size limit (10MB)
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
    
    file_obj = FileAttachment(
        task_id=file.task_id,
        filename=file.filename,
        content_type=file.content_type,
        file_data=file.file_data,
        file_size=file_size,
        uploaded_by=current_user.id
    )
    await db.file_attachments.insert_one(file_obj.dict())
    
    # Create notification for task owner/assignee
    task_owner = await db.users.find_one({"id": task["created_by"]})
    if task_owner and task_owner["id"] != current_user.id:
        notification = Notification(
            user_id=task_owner["id"],
            title="File Uploaded",
            message=f"{current_user.name} uploaded a file to task: {task['title']}",
            type="file_upload",
            task_id=file.task_id,
            project_id=task["project_id"]
        )
        await db.notifications.insert_one(notification.dict())
    
    return file_obj

@api_router.get("/files", response_model=List[FileAttachment])
async def get_files(task_id: str, current_user: User = Depends(get_current_user)):
    # Verify task access
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = await db.projects.find_one({"id": task["project_id"], "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.file_attachments.find({"task_id": task_id}).sort("uploaded_at", -1).to_list(100)
    return [FileAttachment(**file) for file in files]

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str, current_user: User = Depends(get_current_user)):
    file_doc = await db.file_attachments.find_one({"id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Verify access through task
    task = await db.tasks.find_one({"id": file_doc["task_id"]})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = await db.projects.find_one({"id": task["project_id"], "owner_id": current_user.id})
    if not project and file_doc["uploaded_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = await db.file_attachments.delete_one({"id": file_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"message": "File deleted successfully"}

# Comment Routes
@api_router.post("/comments", response_model=Comment)
async def create_comment(comment: CommentCreate, current_user: User = Depends(get_current_user)):
    # Verify task access
    task = await db.tasks.find_one({"id": comment.task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = await db.projects.find_one({"id": task["project_id"], "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    comment_obj = Comment(
        task_id=comment.task_id,
        user_id=current_user.id,
        user_name=current_user.name,
        content=comment.content,
        parent_id=comment.parent_id
    )
    await db.comments.insert_one(comment_obj.dict())
    
    # Create notification for task owner/assignee
    task_owner = await db.users.find_one({"id": task["created_by"]})
    if task_owner and task_owner["id"] != current_user.id:
        notification = Notification(
            user_id=task_owner["id"],
            title="New Comment",
            message=f"{current_user.name} commented on task: {task['title']}",
            type="comment",
            task_id=comment.task_id,
            project_id=task["project_id"]
        )
        await db.notifications.insert_one(notification.dict())
    
    return comment_obj

@api_router.get("/comments", response_model=List[Comment])
async def get_comments(task_id: str, current_user: User = Depends(get_current_user)):
    # Verify task access
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = await db.projects.find_one({"id": task["project_id"], "owner_id": current_user.id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    comments = await db.comments.find({"task_id": task_id}).sort("created_at", 1).to_list(1000)
    return [Comment(**comment) for comment in comments]

@api_router.put("/comments/{comment_id}", response_model=Comment)
async def update_comment(comment_id: str, comment_update: CommentUpdate, current_user: User = Depends(get_current_user)):
    comment = await db.comments.find_one({"id": comment_id, "user_id": current_user.id})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not owned by user")
    
    result = await db.comments.update_one(
        {"id": comment_id},
        {"$set": {"content": comment_update.content, "updated_at": datetime.utcnow()}}
    )
    
    updated_comment = await db.comments.find_one({"id": comment_id})
    return Comment(**updated_comment)

@api_router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, current_user: User = Depends(get_current_user)):
    comment = await db.comments.find_one({"id": comment_id, "user_id": current_user.id})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not owned by user")
    
    result = await db.comments.delete_one({"id": comment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {"message": "Comment deleted successfully"}

# Progress Analytics Routes
@api_router.get("/analytics/progress", response_model=List[ProjectProgress])
async def get_progress_analytics(current_user: User = Depends(get_current_user)):
    projects = await db.projects.find({"owner_id": current_user.id}).to_list(1000)
    result = []
    
    for project in projects:
        tasks = await db.tasks.find({"project_id": project["id"]}).to_list(1000)
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t["status"] == "Done"])
        in_progress_tasks = len([t for t in tasks if t["status"] == "In Progress"])
        todo_tasks = len([t for t in tasks if t["status"] == "To Do"])
        
        # Calculate overdue tasks
        overdue_tasks = 0
        current_date = datetime.utcnow()
        for task in tasks:
            if task.get("due_date") and task["status"] != "Done":
                due_date = task["due_date"] if isinstance(task["due_date"], datetime) else datetime.fromisoformat(task["due_date"].replace('Z', '+00:00'))
                if due_date < current_date:
                    overdue_tasks += 1
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        stats = ProgressStats(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            todo_tasks=todo_tasks,
            completion_rate=round(completion_rate, 2),
            overdue_tasks=overdue_tasks
        )
        
        result.append(ProjectProgress(
            project_id=project["id"],
            project_title=project["title"],
            stats=stats
        ))
    
    return result

@api_router.get("/analytics/overview")
async def get_analytics_overview(current_user: User = Depends(get_current_user)):
    # Get all user's projects
    projects = await db.projects.find({"owner_id": current_user.id}).to_list(1000)
    project_ids = [p["id"] for p in projects]
    
    # Get all tasks for user's projects
    all_tasks = await db.tasks.find({"project_id": {"$in": project_ids}}).to_list(1000)
    
    # Calculate overall statistics
    total_projects = len(projects)
    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t["status"] == "Done"])
    in_progress_tasks = len([t for t in all_tasks if t["status"] == "In Progress"])
    todo_tasks = len([t for t in all_tasks if t["status"] == "To Do"])
    
    # Calculate overdue tasks
    overdue_tasks = 0
    current_date = datetime.utcnow()
    for task in all_tasks:
        if task.get("due_date") and task["status"] != "Done":
            try:
                due_date = task["due_date"] if isinstance(task["due_date"], datetime) else datetime.fromisoformat(task["due_date"].replace('Z', '+00:00'))
                if due_date < current_date:
                    overdue_tasks += 1
            except:
                continue
    
    # Calculate task creation trend (last 7 days)
    week_ago = current_date - timedelta(days=7)
    recent_tasks = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        day_tasks = len([
            t for t in all_tasks 
            if day_start <= (t["created_at"] if isinstance(t["created_at"], datetime) else datetime.fromisoformat(t["created_at"].replace('Z', '+00:00'))) <= day_end
        ])
        
        recent_tasks.append({
            "date": day.strftime("%Y-%m-%d"),
            "tasks_created": day_tasks
        })
    
    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "todo_tasks": todo_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        "recent_tasks_trend": recent_tasks,
        "status_distribution": {
            "To Do": todo_tasks,
            "In Progress": in_progress_tasks,
            "Done": completed_tasks
        }
    }

# Helper function to create due date notifications
async def create_due_date_notifications():
    """Background task to create notifications for upcoming due dates"""
    tomorrow = datetime.utcnow() + timedelta(days=1)
    tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Find tasks due tomorrow that are not completed
    tasks_due_tomorrow = await db.tasks.find({
        "due_date": {"$gte": tomorrow_start, "$lte": tomorrow_end},
        "status": {"$ne": "Done"}
    }).to_list(1000)
    
    for task in tasks_due_tomorrow:
        # Check if notification already exists
        existing_notification = await db.notifications.find_one({
            "user_id": task["created_by"],
            "task_id": task["id"],
            "type": "due_date"
        })
        
        if not existing_notification:
            notification = Notification(
                user_id=task["created_by"],
                title="Task Due Tomorrow",
                message=f"Task '{task['title']}' is due tomorrow",
                type="due_date",
                task_id=task["id"],
                project_id=task["project_id"]
            )
            await db.notifications.insert_one(notification.dict())

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()