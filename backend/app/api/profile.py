"""
Profile API Router — Protected endpoints for retrieving and updating user profile.

All operations enforce JWT authentication. The user's ID is strictly derived
from the token, preventing unauthorized cross-user modifications.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile_service import get_user_profile, update_user_profile

profile_router = APIRouter(prefix="/profile", tags=["Profile"])


@profile_router.get(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user profile",
)
def get_profile_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve authenticated user profile. Returns id, name, email, and createdAt.
    Never exposes passwordHash.
    """
    return get_user_profile(db=db, user_id=current_user.id)


@profile_router.put(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update authenticated user profile",
)
def update_profile_endpoint(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update authenticated user's name and/or email address.
    Ensures email uniqueness across the system.
    """
    return update_user_profile(
        db=db, user_id=current_user.id, profile_in=profile_in
    )
