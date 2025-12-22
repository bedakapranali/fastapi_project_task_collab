from pydantic import BaseModel, Field
import uuid
from datetime import datetime 
from enum import Enum

class RolesEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"

class EmployeeResponseModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    role: str 
    password_hash: str = Field(exclude=True)
    is_verified : bool
    created_at : datetime
    updated_at : datetime


class RoleUpdateSchema(BaseModel):
    role: RolesEnum

