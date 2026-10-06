import uuid
from datetime import datetime, timezone, date as date_type
from sqlalchemy import Column, String, Numeric, DateTime, Date, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_investment_id() -> str:
    return f"inv_{uuid.uuid4().hex[:12]}"

class Investment(Base):
    __tablename__ = "investments"

    id = Column(String(64), primary_key=True, default=generate_investment_id, index=True)
    userId = Column(
        "userId",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    type = Column(String(64), nullable=False)
    # Stored as exact decimal/numeric for accurate financial representation in INR
    investedAmount = Column("investedAmount", Numeric(14, 2), nullable=False)
    currentValue = Column("currentValue", Numeric(14, 2), nullable=False)
    date = Column(Date, nullable=False, default=date_type.today, index=True)
    createdAt = Column(
        "createdAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="investments")

    __table_args__ = (
        CheckConstraint("investedAmount > 0", name="check_positive_invested_amount"),
        CheckConstraint("currentValue >= 0", name="check_non_negative_current_value"),
        Index("idx_investment_user_date", "userId", "date"),
    )

    def __repr__(self) -> str:
        return (
            f"<Investment(id='{self.id}', userId='{self.userId}', "
            f"name='{self.name}', type='{self.type}', "
            f"investedAmount={self.investedAmount}, currentValue={self.currentValue})>"
        )
