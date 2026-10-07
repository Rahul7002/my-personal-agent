from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Shared fields
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

# Request: What the client sends to register
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

# Response: What we return (never expose hashed_password!)
class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True