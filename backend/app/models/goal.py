import uuid
from datetime import datetime, timezone, date as date_type
from sqlalchemy import Column, String, Numeric, DateTime, Date, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_goal_id() -> str:
    return f"gol_{uuid.uuid4().hex[:12]}"


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String(64), primary_key=True, default=generate_goal_id, index=True)
    userId = Column(
        "userId",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    # Stored as exact decimal/numeric for accurate financial representation in INR
    targetAmount = Column("targetAmount", Numeric(14, 2), nullable=False)
    currentAmount = Column("currentAmount", Numeric(14, 2), nullable=False, default=0)
    targetDate = Column("targetDate", Date, nullable=False, index=True)
    monthlyContribution = Column("monthlyContribution", Numeric(14, 2), nullable=False, default=0)
    createdAt = Column(
        "createdAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="goals")

    __table_args__ = (
        CheckConstraint('"targetAmount" > 0', name="check_positive_target_amount"),
        CheckConstraint('"currentAmount" >= 0', name="check_non_negative_current_amount"),
        CheckConstraint('"monthlyContribution" >= 0', name="check_non_negative_monthly_contribution"),
        Index("idx_goal_user_target_date", "userId", "targetDate"),
    )

    def __repr__(self) -> str:
        return (
            f"<Goal(id='{self.id}', userId='{self.userId}', name='{self.name}', "
            f"targetAmount={self.targetAmount}, currentAmount={self.currentAmount}, "
            f"targetDate='{self.targetDate}')>"
        )
