import uuid
from datetime import datetime, timezone, date as date_type
from sqlalchemy import Column, String, Numeric, DateTime, Date, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

TRANSACTION_TYPES = ("income", "expense")

def generate_transaction_id() -> str:
    return f"txn_{uuid.uuid4().hex[:12]}"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(64), primary_key=True, default=generate_transaction_id, index=True)
    userId = Column(
        "userId",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(String(32), nullable=False, index=True)  # "income" | "expense"
    description = Column(String(255), nullable=False)
    # Stored as exact decimal/numeric for accurate financial representation in INR
    amount = Column(Numeric(14, 2), nullable=False)
    category = Column(String(64), nullable=False)
    date = Column(Date, nullable=False, default=date_type.today, index=True)
    source = Column(String(255), nullable=False)
    createdAt = Column(
        "createdAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense')",
            name="check_valid_transaction_type",
        ),
        Index("idx_transaction_user_date", "userId", "date"),
        Index("idx_transaction_user_type", "userId", "type"),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id='{self.id}', userId='{self.userId}', type='{self.type}', amount={self.amount})>"
