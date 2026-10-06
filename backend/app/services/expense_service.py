"""
Expense Service -- Business logic for Expense CRUD with Transaction synchronization.

Every Expense record is mirrored by exactly one Transaction (type="expense").
Both operations happen within the same database transaction to guarantee
atomicity and prevent duplicate transactions.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.transaction import Transaction
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, user_id: str, expense_in: ExpenseCreate) -> Expense:
    """
    Create an Expense record and its corresponding Transaction atomically.
    The Transaction mirrors userId, amount, date, category, and description.
    """
    expense = Expense(
        userId=user_id,
        description=expense_in.description,
        amount=expense_in.amount,
        category=expense_in.category,
        date=expense_in.date,
    )
    db.add(expense)
    # Flush to generate expense.id before creating the linked transaction
    db.flush()

    transaction = Transaction(
        userId=user_id,
        type="expense",
        description=expense_in.description,
        amount=expense_in.amount,
        category=expense_in.category,
        date=expense_in.date,
        source=expense_in.description,
    )
    db.add(transaction)

    db.commit()
    db.refresh(expense)
    return expense


def get_expenses(db: Session, user_id: str) -> List[Expense]:
    """Retrieve all expenses for a given user, ordered by date descending."""
    return (
        db.query(Expense)
        .filter(Expense.userId == user_id)
        .order_by(Expense.date.desc(), Expense.createdAt.desc())
        .all()
    )


def get_expense_by_id(db: Session, expense_id: str, user_id: str) -> Optional[Expense]:
    """
    Retrieve a single expense by ID, scoped to the authenticated user.
    Returns None if not found or not owned by user (caller should raise 404).
    """
    return (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.userId == user_id)
        .first()
    )


def update_expense(
    db: Session, expense: Expense, expense_in: ExpenseUpdate
) -> Expense:
    """
    Update an existing Expense and its corresponding Transaction atomically.
    Only fields supplied in the request body are updated (partial update).
    The matching Transaction is identified by (userId, type, description, amount, category, date).
    """
    # Capture old values for transaction lookup
    old_description = expense.description
    old_amount = expense.amount
    old_category = expense.category
    old_date = expense.date

    # Apply updates to expense
    update_data = expense_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)

    # Find the corresponding transaction and update it
    # Match by user, type, and the OLD financial fields
    txn = (
        db.query(Transaction)
        .filter(
            Transaction.userId == expense.userId,
            Transaction.type == "expense",
            Transaction.description == old_description,
            Transaction.amount == old_amount,
            Transaction.category == old_category,
            Transaction.date == old_date,
        )
        .first()
    )

    if txn:
        if "description" in update_data:
            txn.description = update_data["description"]
            txn.source = update_data["description"]
        if "amount" in update_data:
            txn.amount = update_data["amount"]
        if "category" in update_data:
            txn.category = update_data["category"]
        if "date" in update_data:
            txn.date = update_data["date"]

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense: Expense) -> None:
    """
    Delete an Expense and its corresponding Transaction atomically.
    Both deletions happen within the same database transaction.
    """
    # Find and delete the mirrored transaction
    txn = (
        db.query(Transaction)
        .filter(
            Transaction.userId == expense.userId,
            Transaction.type == "expense",
            Transaction.description == expense.description,
            Transaction.amount == expense.amount,
            Transaction.category == expense.category,
            Transaction.date == expense.date,
        )
        .first()
    )

    if txn:
        db.delete(txn)

    db.delete(expense)
    db.commit()
