"""
Income API Router — Protected CRUD endpoints for Income management.

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
from app.schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomeResponse,
    IncomeDeleteResponse,
)
from app.services.income_service import (
    create_income,
    get_incomes,
    get_income_by_id,
    update_income,
    delete_income,
)

income_router = APIRouter(prefix="/incomes", tags=["Incomes"])


@income_router.post(
    "",
    response_model=IncomeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new income record",
)
def create_income_endpoint(
    income_in: IncomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new Income entry for the authenticated user.
    Automatically creates a corresponding Transaction (type="income").
    """
    income = create_income(db=db, user_id=current_user.id, income_in=income_in)
    return income


@income_router.get(
    "",
    response_model=List[IncomeResponse],
    status_code=status.HTTP_200_OK,
    summary="List all incomes for the current user",
)
def list_incomes_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all Income records belonging to the authenticated user,
    ordered by date descending.
    """
    return get_incomes(db=db, user_id=current_user.id)


@income_router.get(
    "/{income_id}",
    response_model=IncomeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific income record",
)
def get_income_endpoint(
    income_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific Income by ID. Returns 404 if the income
    does not exist or does not belong to the authenticated user.
    """
    income = get_income_by_id(db=db, income_id=income_id, user_id=current_user.id)
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income record not found.",
        )
    return income


@income_router.put(
    "/{income_id}",
    response_model=IncomeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing income record",
)
def update_income_endpoint(
    income_id: str,
    income_in: IncomeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing Income record. Only fields provided in the request body
    are updated. Also updates the corresponding Transaction atomically.
    Returns 404 if the income does not exist or does not belong to the user.
    """
    income = get_income_by_id(db=db, income_id=income_id, user_id=current_user.id)
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income record not found.",
        )
    updated = update_income(db=db, income=income, income_in=income_in)
    return updated


@income_router.delete(
    "/{income_id}",
    response_model=IncomeDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete an income record",
)
def delete_income_endpoint(
    income_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an Income record and its corresponding Transaction atomically.
    Returns 404 if the income does not exist or does not belong to the user.
    """
    income = get_income_by_id(db=db, income_id=income_id, user_id=current_user.id)
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income record not found.",
        )
    deleted_id = income.id
    delete_income(db=db, income=income)
    return IncomeDeleteResponse(
        message="Income record deleted successfully.",
        id=deleted_id,
    )
