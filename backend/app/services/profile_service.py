"""
Profile Service — Logic for managing the authenticated user's profile.

Ensures strict user identity derivation from JWT and unique email validation.
Never exposes or mutates passwordHash.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.profile import ProfileUpdate


def get_user_profile(db: Session, user_id: str) -> User:
    """
    Retrieve the authenticated user's profile.
    Raises 404 if the user does not exist in the database.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User record not found.",
        )
    return user


def update_user_profile(
    db: Session, user_id: str, profile_in: ProfileUpdate
) -> User:
    """
    Update the authenticated user's profile.
    Checks for email collision if email is being modified.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User record not found.",
        )

    # If email is provided and differs from current, ensure it's not taken by another user
    if profile_in.email is not None and profile_in.email.lower() != user.email.lower():
        existing_user = (
            db.query(User)
            .filter(User.email == profile_in.email.lower(), User.id != user.id)
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already in use by another account.",
            )
        user.email = profile_in.email.lower()

    if profile_in.name is not None:
        user.name = profile_in.name.strip()

    db.commit()
    db.refresh(user)
    return user
