"""
Transaction Service -- Read-only query logic for the unified Transactions API.

Transactions are created/updated/deleted exclusively through the Income and
Expense APIs. This service provides filtered, user-scoped read access only.
"""
from datetime import date as date_type
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def get_transactions(
    db: Session,
    user_id: str,
    type_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    date_from: Optional[date_type] = None,
    date_to: Optional[date_type] = None,
) -> List[Transaction]:
    """
    Retrieve all transactions for a given user with optional filters.
    Results are ordered by date descending, then createdAt descending.
    """
    query = db.query(Transaction).filter(Transaction.userId == user_id)

    if type_filter is not None:
        query = query.filter(Transaction.type == type_filter)

    if category_filter is not None:
        query = query.filter(Transaction.category == category_filter)

    if date_from is not None:
        query = query.filter(Transaction.date >= date_from)

    if date_to is not None:
        query = query.filter(Transaction.date <= date_to)

    return (
        query
        .order_by(Transaction.date.desc(), Transaction.createdAt.desc())
        .all()
    )


def get_transaction_by_id(
    db: Session, transaction_id: str, user_id: str
) -> Optional[Transaction]:
    """
    Retrieve a single transaction by ID, scoped to the authenticated user.
    Returns None if not found or not owned by user (caller should raise 404).
    """
    return (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.userId == user_id)
        .first()
    )
