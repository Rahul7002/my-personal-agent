from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.db.session import engine
from app.db.base import Base
from app.models.user import User
from app.db.session import get_db
from app.api.v1.chat import router as chat_router
from app.api.v1.auth import router as auth_router
from app.core.config import settings
# 1. Initialize the FastAPI app instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-creates 'users' table in PostgreSQL if missing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 2. You MUST include it here:
app.include_router(chat_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
def health_check_read_root():
    greeting = "Hello"
    audience = "World"
    full_message = f"{greeting}, {audience}!"
    return {"message": full_message,"status": "ok", "provider": settings.LLM_PROVIDER}

