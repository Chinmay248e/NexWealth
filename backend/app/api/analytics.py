"""
Analytics API Router — Protected endpoint for live financial analytics and aggregations.

All calculations require JWT authentication via the `get_current_user` dependency.
The `userId` is strictly derived from the authenticated user's token.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.analytics_service import get_analytics_summary

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get complete financial analytics summary for the authenticated user",
)
def get_analytics_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns live aggregated analytics for the authenticated user:
    - Core Financial Overview (Income, Expenses, Savings, Savings Rate)
    - Categorized Expense Breakdown (% and amounts)
    - Monthly Cashflow trend (Chronological Income vs Expenses vs Savings)
    - Investment Portfolio Performance (Invested, Current Value, Net Gain, ROI %)
    """
    return get_analytics_summary(db=db, user_id=current_user.id)
