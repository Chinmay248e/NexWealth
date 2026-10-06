"""
Analytics Service — Advanced Financial Calculations and Portfolio Aggregations.

Computes:
1. Financial Overview (Income, Expenses, Savings, Savings Rate)
2. Expense Category Breakdown (amount and percentage share per category)
3. Monthly Cashflow (chronological income, expenses, and net savings by month)
4. Investment Overview (total invested, current valuation, gain/loss, and ROI %)

All calculations use Python Decimal precision and PostgreSQL aggregation.
"""
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.income import Income
from app.models.expense import Expense
from app.models.investment import Investment
from app.schemas.analytics import (
    FinancialOverview,
    CategoryBreakdownItem,
    MonthlyCashflowItem,
    InvestmentOverview,
    AnalyticsSummaryResponse,
)


def get_analytics_summary(db: Session, user_id: str) -> AnalyticsSummaryResponse:
    """
    Compute comprehensive analytics summary for the authenticated user.
    Handles zero-data scenarios cleanly and safely.
    """
    # ──────────────────────────────────────────────────
    # 1. Financial Overview
    # ──────────────────────────────────────────────────
    income_sum = (
        db.query(func.coalesce(func.sum(Income.amount), Decimal("0.00")))
        .filter(Income.userId == user_id)
        .scalar()
    )
    total_income = Decimal(str(income_sum or 0)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    expense_sum = (
        db.query(func.coalesce(func.sum(Expense.amount), Decimal("0.00")))
        .filter(Expense.userId == user_id)
        .scalar()
    )
    total_expenses = Decimal(str(expense_sum or 0)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    available_savings = total_income - total_expenses

    if total_income > Decimal("0.00"):
        savings_rate = ((available_savings / total_income) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        savings_rate = Decimal("0.00")

    overview = FinancialOverview(
        totalIncome=total_income,
        totalExpenses=total_expenses,
        availableSavings=available_savings,
        savingsRate=savings_rate,
    )

    # ──────────────────────────────────────────────────
    # 2. Expense Category Breakdown
    # ──────────────────────────────────────────────────
    cat_query = (
        db.query(Expense.category, func.sum(Expense.amount).label("cat_amount"))
        .filter(Expense.userId == user_id)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    category_breakdown: List[CategoryBreakdownItem] = []
    for cat_name, cat_amt in cat_query:
        amt = Decimal(str(cat_amt or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if total_expenses > Decimal("0.00"):
            pct = ((amt / total_expenses) * Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            pct = Decimal("0.00")
        category_breakdown.append(
            CategoryBreakdownItem(category=cat_name, amount=amt, percentage=pct)
        )

    # ──────────────────────────────────────────────────
    # 3. Monthly Income vs Expenses (Chronological)
    # ──────────────────────────────────────────────────
    user_incomes = (
        db.query(Income.date, Income.amount)
        .filter(Income.userId == user_id)
        .all()
    )
    user_expenses = (
        db.query(Expense.date, Expense.amount)
        .filter(Expense.userId == user_id)
        .all()
    )

    monthly_income = defaultdict(lambda: Decimal("0.00"))
    monthly_expenses = defaultdict(lambda: Decimal("0.00"))
    all_months = set()

    for inc_date, inc_amount in user_incomes:
        month_str = inc_date.strftime("%Y-%m")
        all_months.add(month_str)
        monthly_income[month_str] += Decimal(str(inc_amount or 0))

    for exp_date, exp_amount in user_expenses:
        month_str = exp_date.strftime("%Y-%m")
        all_months.add(month_str)
        monthly_expenses[month_str] += Decimal(str(exp_amount or 0))

    sorted_months = sorted(list(all_months))
    monthly_cashflow: List[MonthlyCashflowItem] = []
    for m in sorted_months:
        inc = monthly_income[m].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        exp = monthly_expenses[m].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        sav = inc - exp
        monthly_cashflow.append(
            MonthlyCashflowItem(
                month=m,
                income=inc,
                expenses=exp,
                savings=sav,
            )
        )

    # ──────────────────────────────────────────────────
    # 4. Investment Overview
    # ──────────────────────────────────────────────────
    invested_sum = (
        db.query(func.coalesce(func.sum(Investment.investedAmount), Decimal("0.00")))
        .filter(Investment.userId == user_id)
        .scalar()
    )
    total_invested = Decimal(str(invested_sum or 0)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    current_val_sum = (
        db.query(func.coalesce(func.sum(Investment.currentValue), Decimal("0.00")))
        .filter(Investment.userId == user_id)
        .scalar()
    )
    current_value = Decimal(str(current_val_sum or 0)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    gain_loss = current_value - total_invested
    if total_invested > Decimal("0.00"):
        return_percent = ((gain_loss / total_invested) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        return_percent = Decimal("0.00")

    investment_overview = InvestmentOverview(
        totalInvested=total_invested,
        currentValue=current_value,
        gainLoss=gain_loss,
        returnPercent=return_percent,
    )

    return AnalyticsSummaryResponse(
        overview=overview,
        categoryBreakdown=category_breakdown,
        monthlyCashflow=monthly_cashflow,
        investmentOverview=investment_overview,
    )
