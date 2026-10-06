import uuid
from datetime import datetime, timezone, date as date_type
from sqlalchemy import Column, String, Numeric, DateTime, Date, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

# Exactly matches NEXWEALTH_DATA_CONTRACT.md section 4.1.3
EXPENSE_CATEGORIES = (
    "Food",
    "Shopping",
    "Transport",
    "Bills",
    "Entertainment",
    "Education",
    "Medical",
    "Travel",
    "Other",
)

def generate_expense_id() -> str:
    return f"exp_{uuid.uuid4().hex[:12]}"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String(64), primary_key=True, default=generate_expense_id, index=True)
    userId = Column(
        "userId",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description = Column(String(255), nullable=False)
    # Stored as exact decimal/numeric for accurate financial representation in INR
    amount = Column(Numeric(14, 2), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    date = Column(Date, nullable=False, default=date_type.today, index=True)
    createdAt = Column(
        "createdAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="expenses")

    __table_args__ = (
        CheckConstraint(
            f"category IN ({','.join([repr(c) for c in EXPENSE_CATEGORIES])})",
            name="check_valid_expense_category",
        ),
        Index("idx_expense_user_date", "userId", "date"),
        Index("idx_expense_user_category", "userId", "category"),
    )

    def __repr__(self) -> str:
        return f"<Expense(id='{self.id}', userId='{self.userId}', category='{self.category}', amount={self.amount})>"
