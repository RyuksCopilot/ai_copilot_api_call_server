from app.db.session import engine
from app.db.base import Base
import app.models.history  # IMPORTANT: import models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
