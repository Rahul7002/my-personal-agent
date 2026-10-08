import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.session import get_db
from app.models.user import User
from app.models.token import RefreshToken
from app.schemas.user import (
    UserCreate,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    AccessTokenResponse,
    LogoutRequest,
    MessageResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    LoginRequest,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# register user API

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

# login api
@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: LoginRequest,  # <-- Uses clean JSON schema
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == payload.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    access_token = create_access_token(subject=str(user.id))
    refresh_token_str, jti, expire_at = create_refresh_token(subject=str(user.id))

    db_token = RefreshToken(
        user_id=user.id,
        token_jti=jti,
        expires_at=expire_at,
        revoked=False
    )
    db.add(db_token)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
    )

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    token_data = decode_refresh_token(payload.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = token_data.get("sub")
    jti = token_data.get("jti")

    # Verify against database record
    query = select(RefreshToken).where(RefreshToken.token_jti == jti)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked or is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check user status
    user_query = select(User).where(User.id == uuid.UUID(user_id_str))
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Issue fresh short-lived access token
    new_access_token = create_access_token(subject=str(user.id))
    return AccessTokenResponse(access_token=new_access_token, token_type="bearer")

@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revokes the refresh token so it cannot be used again."""
    token_data = decode_refresh_token(payload.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token format"
        )

    jti = token_data.get("jti")
    
    # Mark revoked in PostgreSQL
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.token_jti == jti, RefreshToken.user_id == current_user.id)
        .values(revoked=True)
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return MessageResponse(message="Successfully logged out")

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Changes the password for the currently logged-in user and revokes active refresh tokens."""
    # 1. Verify that the current password matches
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # 2. Prevent reusing the exact same password
    if verify_password(payload.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current password"
        )

    # 3. Hash the new password and update the user record
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.add(current_user)

    # 4. Security enhancement: Revoke all existing refresh tokens for this user
    revoke_tokens_stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == current_user.id)
        .values(revoked=True)
    )
    await db.execute(revoke_tokens_stmt)

    await db.commit()

    return MessageResponse(message="Password changed successfully. Please log in again with your new password.")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a password reset token. In production, this emails the link.
    In local development, we print the reset token to the server console.
    """
    query = select(User).where(User.email == payload.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user and user.is_active:
        reset_token = create_password_reset_token(email=user.email)
        
        # During local development, print the token directly to your terminal
        print("\n" + "=" * 60)
        print(f"[DEV ONLY] Password reset token for {user.email}:")
        print(reset_token)
        print("=" * 60 + "\n")
        
        # In production: trigger background task (e.g. Celery / FastMail / SendGrid)

    # Always return 200 OK with identical text to prevent account enumeration
    return MessageResponse(
        message="If this email is registered, instructions to reset your password have been sent."
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verifies the reset token, updates password, and revokes all active sessions."""
    email = verify_password_reset_token(payload.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )

    # 1. Update to the new hashed password
    user.hashed_password = get_password_hash(payload.new_password)
    db.add(user)

    # 2. Invalidate all existing refresh tokens for security
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id)
        .values(revoked=True)
    )
    await db.execute(stmt)
    await db.commit()

    return MessageResponse(message="Password has been successfully reset. You can now log in.")