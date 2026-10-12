from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Key function extracts the client's IP.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=settings.REDIS_URL,
)