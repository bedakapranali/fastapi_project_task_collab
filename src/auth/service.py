from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User
from .schemas import CreateUserModel
from .utils import generate_password_hash
from src.errors import UserNotFound, UserAlreadyExists


class UserService:

    # --------------------------------------------------
    # GET USER BY EMAIL (Single source of truth)
    # --------------------------------------------------
    async def get_user_by_email(
        self,
        user_email: str,
        session: AsyncSession
    ):
        statement = select(User).where(User.email == user_email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exists(self,email:str, session:AsyncSession):
        user  = await self.get_user_by_email(email, session)
        if user is None:
            return False
        else:
            return True
    # --------------------------------------------------
    # CREATE USER
    # --------------------------------------------------
    async def create_user(
        self,
        user_data: CreateUserModel,
        session: AsyncSession
    ):
        # Check if user already exists
        statement = select(User).where(User.email == user_data.email)
        result = await session.exec(statement)
        if result.first():
            raise UserAlreadyExists("User with this email already exists")

        user_dict = user_data.model_dump()

        password = user_dict.pop("password_hash")

        new_user = User(
            **user_dict,
            password_hash=generate_password_hash(password)
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    # --------------------------------------------------
    # UPDATE USER
    # --------------------------------------------------
    async def update_user(
        self,
        user: User,
        user_data: dict,
        session: AsyncSession
    ):
        if not user:
            raise UserNotFound("User not found")

        for key, value in user_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)
        return user
