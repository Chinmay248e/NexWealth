"""
Expense API Router -- Protected CRUD endpoints for Expense management.

All endpoints require JWT authentication via the `get_current_user` dependency.
The `userId` is always derived from the authenticated user's token, never from
request data.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseDeleteResponse,
)
from app.services.expense_service import (
    create_expense,
    get_expenses,
    get_expense_by_id,
    update_expense,
    delete_expense,
)

expense_router = APIRouter(prefix="/expenses", tags=["Expenses"])


@expense_router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense record",
)
def create_expense_endpoint(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new Expense entry for the authenticated user.
    Automatically creates a corresponding Transaction (type="expense").
    """
    expense = create_expense(db=db, user_id=current_user.id, expense_in=expense_in)
    return expense


@expense_router.get(
    "",
    response_model=List[ExpenseResponse],
    status_code=status.HTTP_200_OK,
    summary="List all expenses for the current user",
)
def list_expenses_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all Expense records belonging to the authenticated user,
    ordered by date descending.
    """
    return get_expenses(db=db, user_id=current_user.id)


@expense_router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific expense record",
)
def get_expense_endpoint(
    expense_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific Expense by ID. Returns 404 if the expense
    does not exist or does not belong to the authenticated user.
    """
    expense = get_expense_by_id(db=db, expense_id=expense_id, user_id=current_user.id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense record not found.",
        )
    return expense


@expense_router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing expense record",
)
def update_expense_endpoint(
    expense_id: str,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing Expense record. Only fields provided in the request body
    are updated. Also updates the corresponding Transaction atomically.
    Returns 404 if the expense does not exist or does not belong to the user.
    """
    expense = get_expense_by_id(db=db, expense_id=expense_id, user_id=current_user.id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense record not found.",
        )
    updated = update_expense(db=db, expense=expense, expense_in=expense_in)
    return updated


@expense_router.delete(
    "/{expense_id}",
    response_model=ExpenseDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete an expense record",
)
def delete_expense_endpoint(
    expense_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an Expense record and its corresponding Transaction atomically.
    Returns 404 if the expense does not exist or does not belong to the user.
    """
    expense = get_expense_by_id(db=db, expense_id=expense_id, user_id=current_user.id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense record not found.",
        )
    deleted_id = expense.id
    delete_expense(db=db, expense=expense)
    return ExpenseDeleteResponse(
        message="Expense record deleted successfully.",
        id=deleted_id,
    )
