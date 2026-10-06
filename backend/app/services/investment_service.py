"""
Investment Service — Business logic for Person 3 Investment portfolio CRUD.

Provides isolated database operations for user investment assets.
All operations are scoped to the authenticated user's ID.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.investment import Investment
from app.schemas.investment import InvestmentCreate, InvestmentUpdate


def create_investment(db: Session, user_id: str, investment_in: InvestmentCreate) -> Investment:
    """
    Create an Investment record for the authenticated user.
    """
    investment = Investment(
        userId=user_id,
        name=investment_in.name,
        type=investment_in.type,
        investedAmount=investment_in.investedAmount,
        currentValue=investment_in.currentValue,
        date=investment_in.date,
    )
    db.add(investment)
    db.commit()
    db.refresh(investment)
    return investment


def get_investments(db: Session, user_id: str) -> List[Investment]:
    """Retrieve all investments for a given user, ordered by date descending."""
    return (
        db.query(Investment)
        .filter(Investment.userId == user_id)
        .order_by(Investment.date.desc(), Investment.createdAt.desc())
        .all()
    )


def get_investment_by_id(db: Session, investment_id: str, user_id: str) -> Optional[Investment]:
    """
    Retrieve a single investment by ID, scoped to the authenticated user.
    Returns None if not found or not owned by user (caller should raise 404).
    """
    return (
        db.query(Investment)
        .filter(Investment.id == investment_id, Investment.userId == user_id)
        .first()
    )


def update_investment(
    db: Session, investment: Investment, investment_in: InvestmentUpdate
) -> Investment:
    """
    Update an existing Investment.
    Only fields supplied in the request body are updated (partial update).
    """
    update_data = investment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(investment, field, value)

    db.commit()
    db.refresh(investment)
    return investment


def delete_investment(db: Session, investment: Investment) -> None:
    """
    Delete an Investment record.
    """
    db.delete(investment)
    db.commit()
