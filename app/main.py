from contextlib import asynccontextmanager
from fastapi import FastAPI,Request, status
from app.db.session import engine
from app.db.base import Base
from app.models.user import User
from app.models.token import RefreshToken
from app.db.session import get_db
from app.api.v1.chat import router as chat_router
from app.api.v1.auth import router as auth_router
from app.core.config import settings
# 1. Initialize the FastAPI app instance
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
from app.core.limiter import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-creates 'users' table in PostgreSQL if missing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 1. Attach limiter state
app.state.limiter = limiter

# 2. Custom 429 response handler
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": request.headers.get("retry-after") or "Please wait a moment."
        },
    )

# 3. Add middleware
app.add_middleware(SlowAPIMiddleware)

# 2. You MUST include it here:
app.include_router(chat_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
def health_check_read_root():
    greeting = "Hello"
    audience = "World"
    full_message = f"{greeting}, {audience}!"
    return {"message": full_message,"status": "ok", "provider": settings.LLM_PROVIDER}

