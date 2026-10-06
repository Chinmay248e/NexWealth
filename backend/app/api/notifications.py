"""
Notifications API Router — Protected endpoints for user alerts and notifications.

All endpoints enforce JWT authentication via `get_current_user`.
`userId` is strictly derived from the token, preventing unauthorized access.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationDeleteResponse,
    NotificationReadAllResponse,
)
from app.services.notification_service import (
    get_notifications,
    get_notification_by_id,
    mark_notification_read,
    mark_all_notifications_read,
    delete_notification,
)

notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])


@notification_router.get(
    "",
    response_model=List[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="List all notifications for the authenticated user",
)
def list_notifications_endpoint(
    unreadOnly: bool = Query(False, description="Filter only unread notifications"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all notifications belonging to the authenticated user,
    ordered newest first (createdAt descending).
    """
    return get_notifications(
        db=db, user_id=current_user.id, unread_only=unreadOnly
    )


@notification_router.put(
    "/read-all",
    response_model=NotificationReadAllResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark all unread notifications as read",
)
def mark_all_read_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark all unread notifications belonging to the authenticated user as read.
    """
    count = mark_all_notifications_read(db=db, user_id=current_user.id)
    return NotificationReadAllResponse(
        message="All notifications marked as read.",
        count=count,
    )


@notification_router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific notification",
)
def get_notification_endpoint(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific notification by ID.
    Returns 404 if not found or not owned by user.
    """
    notification = get_notification_by_id(
        db=db, notification_id=notification_id, user_id=current_user.id
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification record not found.",
        )
    return notification


@notification_router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark a specific notification as read",
)
def mark_notification_read_endpoint(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a single notification as read.
    Returns 404 if not found or not owned by user.
    """
    notification = get_notification_by_id(
        db=db, notification_id=notification_id, user_id=current_user.id
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification record not found.",
        )
    return mark_notification_read(db=db, notification=notification)


@notification_router.delete(
    "/{notification_id}",
    response_model=NotificationDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a notification",
)
def delete_notification_endpoint(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a notification record.
    Returns 404 if not found or not owned by user.
    """
    notification = get_notification_by_id(
        db=db, notification_id=notification_id, user_id=current_user.id
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification record not found.",
        )
    deleted_id = notification.id
    delete_notification(db=db, notification=notification)
    return NotificationDeleteResponse(
        message="Notification deleted successfully.",
        id=deleted_id,
    )
