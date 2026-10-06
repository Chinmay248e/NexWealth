from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user in the PostgreSQL database.
    - Validates email format.
    - Rejects duplicate emails (400 Bad Request).
    - Securely hashes password via bcrypt.
    - Never returns or stores plaintext password or passwordHash.
    - New user initializes with zero financial records.
    """
    normalized_email = user_in.email.lower().strip()

    # Check for existing duplicate email
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    # Hash password securely
    hashed_password = get_password_hash(user_in.password)

    # Create new User model instance
    now_utc = datetime.now(timezone.utc)
    new_user = User(
        name=user_in.name.strip(),
        email=normalized_email,
        passwordHash=hashed_password,
        createdAt=now_utc,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and return JWT access token",
)
def login_user(
    login_in: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate user credentials.
    - Verifies password against stored bcrypt hash.
    - Returns JWT bearer access token with userId encoded as subject.
    - Returns safe UserResponse without exposing passwordHash.
    """
    normalized_email = login_in.email.lower().strip()

    user = db.query(User).filter(User.email == normalized_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(login_in.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token with user's ID as subject
    access_token = create_access_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

@auth_router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user identity",
)
def get_authenticated_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Protected route demonstrating the reusable authentication dependency.
    Returns current user details excluding passwordHash.
    """
    return current_user
