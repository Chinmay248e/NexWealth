import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_bank_statement_id() -> str:
    return f"bst_{uuid.uuid4().hex[:12]}"


class BankStatement(Base):
    __tablename__ = "bank_statements"

    id = Column(String(64), primary_key=True, default=generate_bank_statement_id, index=True)
    userId = Column(
        "userId",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fileName = Column("fileName", String(255), nullable=False)
    accountName = Column("accountName", String(255), nullable=False)
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
    user = relationship("User", back_populates="bank_statements")

    __table_args__ = (
        Index("idx_statement_user_date", "userId", "uploadedAt"),
    )

    def __repr__(self) -> str:
        return (
            f"<BankStatement(id='{self.id}', userId='{self.userId}', "
            f"fileName='{self.fileName}', accountName='{self.accountName}', status='{self.status}')>"
        )
