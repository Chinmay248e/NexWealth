"""
Dashboard API Router -- Core Financial Summary and Metrics.

Provides protected endpoints for viewing aggregated financial calculations:
- GET /api/v1/dashboard/summary

All endpoints require JWT authentication via the `get_current_user` dependency.
The `userId` is always extracted from the JWT token and never accepted from
request query parameters or request body.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import get_dashboard_summary

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get core financial summary for the authenticated user",
)
def get_dashboard_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve the authenticated user's core financial summary including:
    - totalIncome: sum of all income records
    - totalExpenses: sum of all expense records
    - availableSavings: totalIncome - totalExpenses
    - savingsRate: (availableSavings / totalIncome) * 100 (0 if totalIncome is 0)
    """
    return get_dashboard_summary(db=db, user_id=current_user.id)
