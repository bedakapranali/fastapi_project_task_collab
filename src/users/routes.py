from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import RoleChecker
from .schemas import EmployeeResponseModel,RoleUpdateSchema
from .services import EmployeeManagementService
from typing import List

user_router = APIRouter()
emp_service = EmployeeManagementService()
role_checker = RoleChecker(["admin"])


@user_router.get("/users/", response_model=List[EmployeeResponseModel], dependencies=[Depends(role_checker)])
async def get_users(session : AsyncSession = Depends(get_session)):
    employees = await emp_service.get_all_employees(session)
    return employees

@user_router.get("/user/{uid}", response_model=EmployeeResponseModel, dependencies=[Depends(role_checker)])
async def get_user_by_uid(uid:str, session:AsyncSession = Depends(get_session)):
    employee = await emp_service.get_employee_by_id(uid, session)
    return employee

@user_router.patch("/user/{uid}/role",response_model=EmployeeResponseModel, dependencies=[Depends(role_checker)])
async def update_user_role(uid:str,update_employee_role:RoleUpdateSchema, session: AsyncSession = Depends(get_session)):
    employee = await emp_service.update_role(uid,update_employee_role,session)
    return employee


@user_router.delete("/user/{uid}",response_model=EmployeeResponseModel, dependencies=[Depends(role_checker)])
async def delete(uid:str, session: AsyncSession = Depends(get_session)):
    employee = await emp_service.delete_user(uid, session)
    return employee

