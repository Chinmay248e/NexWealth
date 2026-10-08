"""
AI Advisor API Router — Conversational intelligence & financial recommendations for Person 2.

All endpoints require JWT authentication.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai_advisor import (
    AdvisorQueryRequest,
    AdvisorQueryResponse,
    AdvisorInsightsResponse,
)
from app.services.ai_advisor_service import (
    process_advisor_query,
    get_advisor_insights_only,
)

ai_advisor_router = APIRouter(prefix="/ai-advisor", tags=["AI Advisor"])


@ai_advisor_router.post(
    "/chat",
    response_model=AdvisorQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query AI Financial Copilot with user financial context",
)
def chat_with_advisor_endpoint(
    req: AdvisorQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an AI response customized to the authenticated user's actual financial records.
    """
    return process_advisor_query(
        db=db,
        user_id=current_user.id,
        query=req.message,
        history=req.history,
    )


@ai_advisor_router.get(
    "/insights",
    response_model=AdvisorInsightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get proactive financial insights and optimization cards",
)
def get_insights_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve proactive financial insight and strategy cards for current user.
    """
    return get_advisor_insights_only(db=db, user_id=current_user.id)
