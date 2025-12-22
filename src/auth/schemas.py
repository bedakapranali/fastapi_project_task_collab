from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List

class CreateUserModel(BaseModel):
    username: str
    email: str
    password_hash: str
    role: str 

class UserResponseModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    role: str 
    password_hash: str = Field(exclude=True)
    is_verified : bool
    created_at : datetime
    updated_at : datetime

class UserLoginModel(BaseModel):
    email : str
    password : str

class EmailModel(BaseModel):
    addresses : List[str]

class PasswordResetModel(BaseModel):
    email:str

class PasswordResetConfirmModel(BaseModel):
    new_password : str
    confirm_new_password : str