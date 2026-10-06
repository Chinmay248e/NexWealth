import uuid
from datetime import datetime, timezone, date as date_type
from sqlalchemy import Column, String, Numeric, DateTime, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_income_id() -> str:
    return f"inc_{uuid.uuid4().hex[:12]}"

class Income(Base):
    __tablename__ = "incomes"

    id = Column(String(64), primary_key=True, default=generate_income_id, index=True)
    userId = Column(
        "userId",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source = Column(String(255), nullable=False)
    # Stored as exact decimal/numeric for accurate financial representation in INR
    amount = Column(Numeric(14, 2), nullable=False)
    date = Column(Date, nullable=False, default=date_type.today, index=True)
    createdAt = Column(
        "createdAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="incomes")

    __table_args__ = (
        Index("idx_income_user_date", "userId", "date"),
    )

    def __repr__(self) -> str:
        return f"<Income(id='{self.id}', userId='{self.userId}', source='{self.source}', amount={self.amount})>"
