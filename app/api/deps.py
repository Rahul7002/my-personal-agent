import uuid
import jwt
from fastapi import Depends, HTTPException, status
# 1. Replace OAuth2PasswordBearer with HTTPBearer and HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

# 2. Instantiate HTTPBearer instead of OAuth2PasswordBearer
# This tells Swagger UI to prompt directly for the Bearer token without the username/password form.
http_bearer = HTTPBearer()

async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 3. Extract the raw token string from the credentials object
    token = auth.credentials

    try:
        # Decode the JWT token using your secret key and algorithm
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Prevent refresh tokens from being used as access tokens
        if payload.get("type") != "access":
            raise credentials_exception

        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    # Query the database to ensure the user still exists
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user