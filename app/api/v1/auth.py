from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Check if email already exists
    query = select(User).where(User.email == payload.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists."
        )

    # 2. Hash the password
    hashed_pwd = get_password_hash(payload.password)

    # 3. Create the database record
    new_user = User(
        email=payload.email,
        hashed_password=hashed_pwd,
        full_name=payload.full_name,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user