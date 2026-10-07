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

# Adding token schemas
# Login response containing both tokens
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Payload client sends to POST /auth/refresh
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Payload returned when successfully refreshing
class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LogoutRequest(BaseModel):
    refresh_token: str

class MessageResponse(BaseModel):
    message: str

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters")