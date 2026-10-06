import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_notification_id() -> str:
    return f"ntf_{uuid.uuid4().hex[:12]}"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(64), primary_key=True, default=generate_notification_id, index=True)
    userId = Column(
        "userId",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(String(64), nullable=False, default="info")
    title = Column(String(255), nullable=False)
    message = Column(String(1024), nullable=False)
    read = Column(Boolean, default=False, nullable=False, index=True)
    createdAt = Column(
        "createdAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationship
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("idx_notification_user_created", "userId", "createdAt"),
        Index("idx_notification_user_read", "userId", "read"),
    )

    def __repr__(self) -> str:
        return f"<Notification(id='{self.id}', userId='{self.userId}', title='{self.title}', read={self.read})>"
