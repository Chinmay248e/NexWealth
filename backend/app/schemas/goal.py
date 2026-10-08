from datetime import datetime, date as date_type
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class GoalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Goal name/title")
    targetAmount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        max_digits=14,
        description="Target amount in INR (must be positive Decimal)",
    )
    currentAmount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
        max_digits=14,
        description="Accumulated amount in INR (must be >= 0)",
    )
    targetDate: date_type = Field(..., description="Target completion date (YYYY-MM-DD)")
    monthlyContribution: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
        max_digits=14,
        description="Planned monthly contribution in INR",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Goal name cannot be blank.")
        return stripped


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    targetAmount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, max_digits=14)
    currentAmount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, max_digits=14)
    targetDate: Optional[date_type] = None
    monthlyContribution: Optional[Decimal] = Field(None, ge=0, decimal_places=2, max_digits=14)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Goal name cannot be blank.")
            return stripped
        return v


class GoalAddFunds(BaseModel):
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        max_digits=14,
        description="Amount in INR to deposit toward this goal",
    )


class GoalResponse(GoalBase):
    id: str
    userId: str
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class GoalDeleteResponse(BaseModel):
    message: str
    id: str
