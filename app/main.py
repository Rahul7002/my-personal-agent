from fastapi import FastAPI
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