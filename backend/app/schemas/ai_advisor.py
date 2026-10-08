from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant' or 'system'")
    content: str = Field(..., min_length=1, description="Message text content")


class AdvisorQueryRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User query / prompt")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Prior conversation messages")


class AdvisorInsightCard(BaseModel):
    id: str
    type: str = Field(..., description="'optimization' | 'strategy' | 'warning' | 'achievement'")
    title: str
    description: str
    tag: str
    impact: Optional[str] = None


class FinancialContextSummary(BaseModel):
    totalIncome: Decimal
    totalExpenses: Decimal
    availableSavings: Decimal
    savingsRate: float
    totalInvestments: Decimal
    totalGoalsTarget: Decimal
    totalGoalsSaved: Decimal
    topExpenseCategory: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class AdvisorQueryResponse(BaseModel):
    reply: str
    insights: List[AdvisorInsightCard]
    contextSummary: FinancialContextSummary
    model: str = "NexAdvisor Neural Engine"


class AdvisorInsightsResponse(BaseModel):
    insights: List[AdvisorInsightCard]
    summary: FinancialContextSummary
