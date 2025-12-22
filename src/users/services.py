from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User
from .schemas import RoleUpdateSchema
from src.errors import EmployeeNotFound


class EmployeeManagementService:

    # --------------------------------------------------
    # GET ALL EMPLOYEES
    # --------------------------------------------------
    async def get_all_employees(self, session: AsyncSession):
        statement = select(User).order_by(User.created_at.desc())
        result = await session.exec(statement)
        return result.all()

    # --------------------------------------------------
    # GET EMPLOYEE BY ID (Single source of truth)
    # --------------------------------------------------
    async def get_employee_by_id(self, uid: str, session: AsyncSession):
        statement = select(User).where(User.uid == uid)
        result = await session.exec(statement)
        employee = result.first()

        if not employee:
            raise EmployeeNotFound("Employee not found")

        return employee

    # --------------------------------------------------
    # UPDATE EMPLOYEE ROLE
    # --------------------------------------------------
    async def update_role(
        self,
        uid: str,
        update_employee_role: RoleUpdateSchema,
        session: AsyncSession
    ):
        employee = await self.get_employee_by_id(uid, session)

        update_data = update_employee_role.model_dump()
        employee.role = update_data["role"]

        await session.commit()
        await session.refresh(employee)
        return employee

    # --------------------------------------------------
    # DELETE EMPLOYEE
    # --------------------------------------------------
    async def delete_user(self, uid: str, session: AsyncSession):
        employee = await self.get_employee_by_id(uid, session)

        await session.delete(employee)
        await session.commit()
        return employee
