from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://neondb_owner:npg_l3MLntXUxGN9@ep-royal-pond-adxjo5op-pooler.c-2.us-east-1.aws.neon.tech/neondb"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
