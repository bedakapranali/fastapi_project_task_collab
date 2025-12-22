from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime
import uuid
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    username: str
    email: str
    password_hash: str
    role: str = Field(default="user")
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now))

    # FIXED RELATIONSHIPS
    created_tasks: list["Task"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[Task.created_by]"}
    )
    assigned_tasks: list["Task"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "[Task.assigned_to]"}
    )


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    title: str
    description: str
    status: str = Field(default="pending")      # pending, in_progress, completed
    priority: str = Field(default="medium")     # low, medium, high
    due_date: datetime | None = None
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now))

    # Foreign Keys
    created_by: uuid.UUID = Field(foreign_key="users.uid")
    assigned_to: uuid.UUID | None = Field(default=None, foreign_key="users.uid")

    # FIXED RELATIONSHIPS
    creator: User = Relationship(
        back_populates="created_tasks",
        sa_relationship_kwargs={"foreign_keys": "[Task.created_by]"}
    )
    assignee: User = Relationship(
        back_populates="assigned_tasks",
        sa_relationship_kwargs={"foreign_keys": "[Task.assigned_to]"}
    )
