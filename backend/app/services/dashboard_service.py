"""
Dashboard Service -- Core Financial Calculations logic.

Calculates aggregated financial metrics:
- totalIncome: SUM(Income.amount) for current user
- totalExpenses: SUM(Expense.amount) for current user
- availableSavings: totalIncome - totalExpenses
- savingsRate: (availableSavings / totalIncome) * 100 (0 if totalIncome == 0)

All calculations are performed using exact Decimal arithmetic.
"""
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.income import Income
from app.models.expense import Expense
from app.schemas.dashboard import DashboardSummaryResponse


def get_dashboard_summary(db: Session, user_id: str) -> DashboardSummaryResponse:
    """
    Calculate and return the core financial summary for a user.
    Uses SQL aggregation and Python Decimal arithmetic to prevent
    floating-point inaccuracies.
    """
    # 1. Total income: SUM of all Income.amount belonging to the authenticated user
    income_sum = (
        db.query(func.coalesce(func.sum(Income.amount), Decimal("0.00")))
        .filter(Income.userId == user_id)
        .scalar()
    )
    total_income = Decimal(str(income_sum or 0)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # 2. Total expenses: SUM of all Expense.amount belonging to the authenticated user
    expense_sum = (
        db.query(func.coalesce(func.sum(Expense.amount), Decimal("0.00")))
        .filter(Expense.userId == user_id)
        .scalar()
    )
    total_expenses = Decimal(str(expense_sum or 0)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # 3. Available savings = totalIncome - totalExpenses
    available_savings = total_income - total_expenses

    # 4. Savings rate = (availableSavings / totalIncome) * 100 (0 if totalIncome == 0)
    if total_income > Decimal("0.00"):
        savings_rate = ((available_savings / total_income) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        savings_rate = Decimal("0.00")

    return DashboardSummaryResponse(
        totalIncome=total_income,
        totalExpenses=total_expenses,
        availableSavings=available_savings,
        savingsRate=savings_rate,
    )
