"""
Notification Service — Business logic for user alerts and system notifications.

All operations are scoped to the authenticated user's ID.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


def create_notification(
    db: Session,
    user_id: str,
    type: str = "info",
    title: str = "",
    message: str = "",
    read: bool = False,
) -> Notification:
    """
    Create a notification entry for a user.
    """
    notification = Notification(
        userId=user_id,
        type=type,
        title=title,
        message=message,
        read=read,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notifications(
    db: Session, user_id: str, unread_only: bool = False
) -> List[Notification]:
    """
    Retrieve notifications for a given user, ordered newest first by createdAt.
    If unread_only is True, filters to read == False.
    """
    query = db.query(Notification).filter(Notification.userId == user_id)
    if unread_only:
        query = query.filter(Notification.read == False)
    return query.order_by(Notification.createdAt.desc()).all()


def get_notification_by_id(
    db: Session, notification_id: str, user_id: str
) -> Optional[Notification]:
    """
    Retrieve a single notification by ID scoped to the user.
    Returns None if missing or not owned by user.
    """
    return (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.userId == user_id)
        .first()
    )


def mark_notification_read(db: Session, notification: Notification) -> Notification:
    """
    Mark a single notification as read.
    """
    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_notifications_read(db: Session, user_id: str) -> int:
    """
    Mark all unread notifications for a user as read.
    Returns the count of updated notifications.
    """
    count = (
        db.query(Notification)
        .filter(Notification.userId == user_id, Notification.read == False)
        .update({Notification.read: True}, synchronize_session="fetch")
    )
    db.commit()
    return count


def delete_notification(db: Session, notification: Notification) -> None:
    """
    Delete a notification record.
    """
    db.delete(notification)
    db.commit()
