from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.api.v1.chat import router as chat_router
from app.core.config import settings
# 1. Initialize the FastAPI app instance
app = FastAPI(title=settings.PROJECT_NAME)

# 2. You MUST include it here:
app.include_router(chat_router, prefix="/api/v1")

# 2. Define a route for the root URL ("/") using the GET HTTP method
# @app.get("/")
# def health_check():
#     return {"status": "ok", "provider": settings.LLM_PROVIDER}

@app.get("/")
def health_check_read_root():
    greeting = "Hello"
    audience = "World"
    full_message = f"{greeting}, {audience}!"
    return {"message": full_message,"status": "ok", "provider": settings.LLM_PROVIDER}


@app.get("/health/db", tags=["Health"])
async def db_health_check(db: AsyncSession = Depends(get_db)):
    # Execute a simple 1-byte raw query to verify socket connection
    result = await db.execute(text("SELECT 1"))
    value = result.scalar()
    return {"status": "connected", "query_result": value}

# @app.get("/debug-routes")
# def debug_routes():
#     routes_info = []
#     for route in app.routes:
#         if hasattr(route, "path"):
#             routes_info.append({
#                 "path": route.path,
#                 "name": getattr(route, "name", None),
#                 "methods": list(getattr(route, "methods", []))
#             })
#     return routes_info