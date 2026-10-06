"""
Transactions API Router -- Read-only protected endpoints for unified transaction view.

Transactions are created/updated/deleted exclusively through the Income and
Expense APIs. This router provides filtered, user-scoped read access only.

All endpoints require JWT authentication via the `get_current_user` dependency.
The `userId` is always derived from the authenticated user's token, never from
request data or query parameters.
"""
from datetime import date as date_type
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.transaction import TransactionResponse
from app.services.transaction_service import (
    get_transactions,
    get_transaction_by_id,
)

transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])


@transaction_router.get(
    "",
    response_model=List[TransactionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all transactions for the current user",
)
def list_transactions_endpoint(
    type: Optional[str] = Query(
        None,
        description="Filter by transaction type: 'income' or 'expense'",
        pattern="^(income|expense)$",
    ),
    category: Optional[str] = Query(
        None,
        description="Filter by category (exact match)",
    ),
    date_from: Optional[date_type] = Query(
        None,
        description="Filter transactions on or after this date (YYYY-MM-DD)",
    ),
    date_to: Optional[date_type] = Query(
        None,
        description="Filter transactions on or before this date (YYYY-MM-DD)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all Transaction records belonging to the authenticated user.
    Supports optional filtering by type, category, date_from, and date_to.
    Results are ordered by date descending, then createdAt descending.
    """
    # Validate date range
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from must not be after date_to.",
        )

    return get_transactions(
        db=db,
        user_id=current_user.id,
        type_filter=type,
        category_filter=category,
        date_from=date_from,
        date_to=date_to,
    )


@transaction_router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific transaction",
)
def get_transaction_endpoint(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific Transaction by ID. Returns 404 if the transaction
    does not exist or does not belong to the authenticated user.
    """
    txn = get_transaction_by_id(
        db=db, transaction_id=transaction_id, user_id=current_user.id
    )
    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found.",
        )
    return txn
