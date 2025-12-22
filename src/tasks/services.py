from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime
from typing import Optional

from src.db.models import Task
from .schemas import TaskCreate, TaskUpdate
from src.errors import TaskNotFound

from src.mail import mail, create_message
from src.users.services import EmployeeManagementService

auth_service = EmployeeManagementService()


class TaskService:

    async def create_task(
        self,
        task_data: TaskCreate,
        session: AsyncSession,
        current_user
    ):
        task_create_dict = task_data.model_dump()
        assigned_to = task_create_dict.get("assigned_to")

        new_task = Task(
            **task_create_dict,
            created_by=current_user.uid
        )

        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

        # Send email AFTER successful DB commit
        if assigned_to:
            await self.send_assignment_email(
                task=new_task,
                user_uid=assigned_to,
                session=session
            )

        return new_task

    # --------------------------------------------------
    # GET TASK BY ID (Single source of truth)
    # --------------------------------------------------
    async def get_task_by_id(self, task_id: str, session: AsyncSession):
        statement = select(Task).where(Task.uid == task_id)
        result = await session.exec(statement)
        task = result.first()

        if not task:
            raise TaskNotFound("Task not found")

        return task

    # --------------------------------------------------
    # UPDATE TASK
    # --------------------------------------------------
    async def update_task_fields(
        self,
        task_uid: str,
        update_task_data: TaskUpdate,
        session: AsyncSession
    ):
        task = await self.get_task_by_id(task_uid, session)

        old_assignee = task.assigned_to
        task_data = update_task_data.model_dump(exclude_unset=True)

        for key, value in task_data.items():
            setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        await session.commit()

        new_assigned_to = task_data.get("assigned_to")
        if "assigned_to" in task_data and new_assigned_to != old_assignee:
            if new_assigned_to is not None:
                await self.send_assignment_email(
                    task=task,
                    user_uid=new_assigned_to,
                    session=session
                )

        await session.refresh(task)
        return task

    # --------------------------------------------------
    # GET ALL TASKS (Pagination + Filters + User-specific)
    # --------------------------------------------------
    async def get_all_tasks(
        self,
        session: AsyncSession,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        current_user=None,  # Add current_user parameter
        show_all: bool = False  # Add show_all parameter for managers/admins
    ):
        statement = select(Task)

        # If current_user is provided and not showing all tasks,
        # regular users can only see tasks assigned to them or created by them
        if current_user and not show_all and current_user.role in ["user", "employee"]:
            statement = statement.where(
                (Task.assigned_to == current_user.uid) | 
                (Task.created_by == current_user.uid)
            )

        if status:
            statement = statement.where(Task.status == status)

        if priority:
            statement = statement.where(Task.priority == priority)

        if assignee:
            statement = statement.where(Task.assigned_to == assignee)

        result = await session.exec(statement)
        all_tasks = result.all()
        total = len(all_tasks)

        offset = (page - 1) * limit
        statement = statement.offset(offset).limit(limit)

        result = await session.exec(statement)
        tasks = result.all()

        return tasks, total

    # --------------------------------------------------
    # DELETE TASK
    # --------------------------------------------------
    async def delete_task(self, task_uid: str, session: AsyncSession):
        task = await self.get_task_by_id(task_uid, session)
        await session.delete(task)
        await session.commit()
        return task

    # --------------------------------------------------
    # SEND ASSIGNMENT EMAIL
    # --------------------------------------------------
    async def send_assignment_email(
        self,
        task: Task,
        user_uid: str,
        session: AsyncSession
    ):
        user = await auth_service.get_employee_by_id(user_uid, session)

        if not user:
            return

        html = f"""
        <h2>New Task Assigned</h2>
        <p>Hello {user.username},</p>
        <p>You have been assigned a new task:</p>
        <ul>
            <li><b>Title:</b> {task.title}</li>
            <li><b>Due Date:</b> {task.due_date}</li>
            <li><b>Status:</b> {task.status}</li>
        </ul>
        """

        message = create_message(
            recipients=[user.email],
            subject="You have been assigned a task",
            body=html
        )

        await mail.send_message(message)