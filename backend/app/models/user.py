import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_user_id() -> str:
    return f"usr_{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=generate_user_id, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    passwordHash = Column("passwordHash", String(255), nullable=False)
    createdAt = Column(
        "createdAt",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships (1-to-Many)
    incomes = relationship(
        "Income",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    expenses = relationship(
        "Expense",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Person 3 Relationships
    investments = relationship(
        "Investment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Person 2 Relationships
    goals = relationship(
        "Goal",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    bank_statements = relationship(
        "BankStatement",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(id='{self.id}', name='{self.name}', email='{self.email}')>"
