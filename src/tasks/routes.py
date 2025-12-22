from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from src.db.main import get_session
from src.auth.dependencies import RoleChecker, get_current_user
from src.db.models import User

from .schemas import TaskCreate, TaskResponse, TaskUpdate
from .services import TaskService
from src.errors import TaskNotFound

# --------------------------------------------------
# Router & Service
# --------------------------------------------------

task_router = APIRouter()
task_service = TaskService()

# --------------------------------------------------
# Role Checkers
# --------------------------------------------------

manager_admin = RoleChecker(["manager", "admin"])
admin_only = RoleChecker(["admin"])

# --------------------------------------------------
# Routes
# --------------------------------------------------

# CREATE TASK - Only manager & admin can create tasks
@task_router.post(
    "/create_task",
    response_model=TaskResponse,
    dependencies=[Depends(manager_admin)]
)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await task_service.create_task(task_data, session, current_user)


# GET ALL TASKS - Any logged-in user can view tasks
@task_router.post("/all")
async def get_all_tasks(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    show_all: bool = False,  # Add this parameter
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),  # Make this required
):
    # Regular users can't see all tasks even if they pass show_all=True
    if current_user.role in ["user", "employee"]:
        show_all = False
    
    tasks, total = await task_service.get_all_tasks(
        session=session,
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        assignee=assignee,
        current_user=current_user,  # Pass current_user
        show_all=show_all  # Pass show_all
    )
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "tasks": tasks,
    }


# GET TASK BY ID - Any logged-in user can view a task
@task_router.get(
    "/{task_id}",
    response_model=TaskResponse
)
async def get_task_by_id(
    task_id: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    try:
        return await task_service.get_task_by_id(task_id, session)
    except TaskNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


# UPDATE TASK - Manager & admin only
@task_router.post(
    "/update_task",
    response_model=TaskResponse,
    
)
async def update_task(
    task_uid: str,
    update_task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    try:
        return await task_service.update_task_fields(task_uid, update_task_data, session)
    except TaskNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


# DELETE TASK - Admin only
@task_router.delete(
    "/delete_task",
    dependencies=[Depends(admin_only)]
)
async def delete_task(
    task_uid: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    try:
        task = await task_service.delete_task(task_uid, session)
        return {
            "message": "Task deleted successfully",
            "task": task,
        }
    except TaskNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))