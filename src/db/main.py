from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.config import config_obj

async_engine = AsyncEngine(
    create_engine(
        url = config_obj.DATABASE_URL,
        echo=True
    )
)

async def get_session() -> AsyncEngine:
    Session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session