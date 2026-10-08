import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_document_id() -> str:
    return f"doc_{uuid.uuid4().hex[:12]}"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, default=generate_document_id, index=True)
    userId = Column(
        "userId",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fileName = Column("fileName", String(255), nullable=False)
    documentType = Column("documentType", String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="uploaded")
    uploadedAt = Column(
        "uploadedAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    createdAt = Column(
        "createdAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="documents")

    __table_args__ = (
        Index("idx_document_user_date", "userId", "uploadedAt"),
    )

    def __repr__(self) -> str:
        return (
            f"<Document(id='{self.id}', userId='{self.userId}', "
            f"fileName='{self.fileName}', documentType='{self.documentType}', status='{self.status}')>"
        )
