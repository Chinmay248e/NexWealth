"""
Expense Pydantic Schemas — Request/Response validation for Expense endpoints.

Category is strictly validated against the allowed list from
NEXWEALTH_DATA_CONTRACT.md section 4.1.3.
"""
from datetime import datetime, date as date_type
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

ALLOWED_CATEGORIES = (
    "Food",
    "Shopping",
    "Transport",
    "Bills",
    "Entertainment",
    "Education",
    "Medical",
    "Travel",
    "Other",
)


class ExpenseBase(BaseModel):
    description: str = Field(
        ..., min_length=1, max_length=255,
        description="Expense description / narration",
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        max_digits=14,
        description="Monetary amount in INR (must be positive Decimal)",
    )
    category: str = Field(
        ..., min_length=1, max_length=64,
        description="Expense category (must be one of the allowed categories)",
    )
    date: date_type = Field(
        default_factory=date_type.today,
        description="Date the expense occurred (YYYY-MM-DD)",
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Expense description cannot be blank.")
        return stripped

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {', '.join(ALLOWED_CATEGORIES)}"
            )
        return v


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, max_digits=14)
    category: Optional[str] = Field(None, min_length=1, max_length=64)
    date: Optional[date_type] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Expense description cannot be blank.")
            return stripped
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {', '.join(ALLOWED_CATEGORIES)}"
            )
        return v


class ExpenseResponse(ExpenseBase):
    id: str
    userId: str
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class ExpenseDeleteResponse(BaseModel):
    message: str
    id: str
