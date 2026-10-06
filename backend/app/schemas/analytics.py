from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict

class FinancialOverview(BaseModel):
    totalIncome: Decimal
    totalExpenses: Decimal
    availableSavings: Decimal
    savingsRate: Decimal

class CategoryBreakdownItem(BaseModel):
    category: str
    amount: Decimal
    percentage: Decimal

class MonthlyCashflowItem(BaseModel):
    month: str  # YYYY-MM format suitable for chronological charting
    income: Decimal
    expenses: Decimal
    savings: Decimal

class InvestmentOverview(BaseModel):
    totalInvested: Decimal
    currentValue: Decimal
    gainLoss: Decimal
    returnPercent: Decimal

class AnalyticsSummaryResponse(BaseModel):
    overview: FinancialOverview
    categoryBreakdown: List[CategoryBreakdownItem]
    monthlyCashflow: List[MonthlyCashflowItem]
    investmentOverview: InvestmentOverview

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
