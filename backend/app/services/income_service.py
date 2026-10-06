"""
Income Service — Business logic for Income CRUD with Transaction synchronization.

Every Income record is mirrored by exactly one Transaction (type="income").
Both operations happen within the same database transaction to guarantee
atomicity and prevent duplicate transactions.
"""
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.income import Income
from app.models.transaction import Transaction
from app.schemas.income import IncomeCreate, IncomeUpdate


def create_income(db: Session, user_id: str, income_in: IncomeCreate) -> Income:
    """
    Create an Income record and its corresponding Transaction atomically.
    The Transaction mirrors all financial fields from the Income.
    """
    income = Income(
        userId=user_id,
        source=income_in.source,
        amount=income_in.amount,
        date=income_in.date,
    )
    db.add(income)
    # Flush to generate income.id before creating the linked transaction
    db.flush()

    transaction = Transaction(
        userId=user_id,
        type="income",
        description=f"Income: {income_in.source}",
        amount=income_in.amount,
        category="Income",
        date=income_in.date,
        source=income_in.source,
    )
    db.add(transaction)

    db.commit()
    db.refresh(income)
    return income


def get_incomes(db: Session, user_id: str) -> List[Income]:
    """Retrieve all incomes for a given user, ordered by date descending."""
    return (
        db.query(Income)
        .filter(Income.userId == user_id)
        .order_by(Income.date.desc(), Income.createdAt.desc())
        .all()
    )


def get_income_by_id(db: Session, income_id: str, user_id: str) -> Optional[Income]:
    """
    Retrieve a single income by ID, scoped to the authenticated user.
    Returns None if not found or not owned by user (caller should raise 404).
    """
    return (
        db.query(Income)
        .filter(Income.id == income_id, Income.userId == user_id)
        .first()
    )


def update_income(
    db: Session, income: Income, income_in: IncomeUpdate
) -> Income:
    """
    Update an existing Income and its corresponding Transaction atomically.
    Only fields supplied in the request body are updated (partial update).
    The matching Transaction is identified by (userId, type, source, amount, date).
    """
    # Capture old values for transaction lookup
    old_source = income.source
    old_amount = income.amount
    old_date = income.date

    # Apply updates to income
    update_data = income_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(income, field, value)

    # Find the corresponding transaction and update it
    # Match by user, type, and the OLD financial fields
    txn = (
        db.query(Transaction)
        .filter(
            Transaction.userId == income.userId,
            Transaction.type == "income",
            Transaction.source == old_source,
            Transaction.amount == old_amount,
            Transaction.date == old_date,
        )
        .first()
    )

    if txn:
        if "source" in update_data:
            txn.source = update_data["source"]
            txn.description = f"Income: {update_data['source']}"
        if "amount" in update_data:
            txn.amount = update_data["amount"]
        if "date" in update_data:
            txn.date = update_data["date"]

    db.commit()
    db.refresh(income)
    return income


def delete_income(db: Session, income: Income) -> None:
    """
    Delete an Income and its corresponding Transaction atomically.
    Both deletions happen within the same database transaction.
    """
    # Find and delete the mirrored transaction
    txn = (
        db.query(Transaction)
        .filter(
            Transaction.userId == income.userId,
            Transaction.type == "income",
            Transaction.source == income.source,
            Transaction.amount == income.amount,
            Transaction.date == income.date,
        )
        .first()
    )

    if txn:
        db.delete(txn)

    db.delete(income)
    db.commit()
