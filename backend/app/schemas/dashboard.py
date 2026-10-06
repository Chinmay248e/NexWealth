from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class DashboardSummaryResponse(BaseModel):
    totalIncome: Decimal = Field(
        ...,
        description="Total income amount in INR",
    )
    totalExpenses: Decimal = Field(
        ...,
        description="Total expenses amount in INR",
    )
    availableSavings: Decimal = Field(
        ...,
        description="Available savings amount (totalIncome - totalExpenses) in INR",
    )
    savingsRate: Decimal = Field(
        ...,
        description="Savings rate percentage ((availableSavings / totalIncome) * 100)",
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
