"""
Investment API Router — Protected CRUD endpoints for Person 3 Investment management.

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
from app.schemas.investment import (
    InvestmentCreate,
    InvestmentUpdate,
    InvestmentResponse,
    InvestmentDeleteResponse,
)
from app.services.investment_service import (
    create_investment,
    get_investments,
    get_investment_by_id,
    update_investment,
    delete_investment,
)

investment_router = APIRouter(prefix="/investments", tags=["Investments"])


@investment_router.post(
    "",
    response_model=InvestmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new investment record",
)
def create_investment_endpoint(
    investment_in: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new Investment entry for the authenticated user.
    """
    investment = create_investment(db=db, user_id=current_user.id, investment_in=investment_in)
    return investment


@investment_router.get(
    "",
    response_model=List[InvestmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List all investments for the current user",
)
def list_investments_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all Investment records belonging to the authenticated user,
    ordered by date descending.
    """
    return get_investments(db=db, user_id=current_user.id)


@investment_router.get(
    "/{investment_id}",
    response_model=InvestmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific investment record",
)
def get_investment_endpoint(
    investment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific Investment by ID. Returns 404 if the investment
    does not exist or does not belong to the authenticated user.
    """
    investment = get_investment_by_id(
        db=db, investment_id=investment_id, user_id=current_user.id
    )
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment record not found.",
        )
    return investment


@investment_router.put(
    "/{investment_id}",
    response_model=InvestmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing investment record",
)
def update_investment_endpoint(
    investment_id: str,
    investment_in: InvestmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing Investment record. Only fields provided in the request body
    are updated. Returns 404 if the investment does not exist or does not belong to the user.
    """
    investment = get_investment_by_id(
        db=db, investment_id=investment_id, user_id=current_user.id
    )
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment record not found.",
        )
    updated = update_investment(
        db=db, investment=investment, investment_in=investment_in
    )
    return updated


@investment_router.delete(
    "/{investment_id}",
    response_model=InvestmentDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete an investment record",
)
def delete_investment_endpoint(
    investment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an Investment record.
    Returns 404 if the investment does not exist or does not belong to the user.
    """
    investment = get_investment_by_id(
        db=db, investment_id=investment_id, user_id=current_user.id
    )
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment record not found.",
        )
    deleted_id = investment.id
    delete_investment(db=db, investment=investment)
    return InvestmentDeleteResponse(
        message="Investment record deleted successfully.",
        id=deleted_id,
    )
