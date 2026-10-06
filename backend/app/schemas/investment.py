from datetime import datetime, date as date_type
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class InvestmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Investment asset name/title")
    type: str = Field(..., min_length=1, max_length=64, description="Asset class/type (e.g., Mutual Fund, Stock, FD, Gold)")
    investedAmount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        max_digits=14,
        description="Total principal invested in INR (must be positive Decimal)",
    )
    currentValue: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        max_digits=14,
        description="Current market valuation in INR (must be zero or positive Decimal)",
    )
    date: date_type = Field(default_factory=date_type.today, description="Investment date (YYYY-MM-DD)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Investment name cannot be blank.")
        return stripped

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Investment type cannot be blank.")
        return stripped

class InvestmentCreate(InvestmentBase):
    pass

class InvestmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, min_length=1, max_length=64)
    investedAmount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, max_digits=14)
    currentValue: Optional[Decimal] = Field(None, ge=0, decimal_places=2, max_digits=14)
    date: Optional[date_type] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Investment name cannot be blank.")
            return stripped
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Investment type cannot be blank.")
            return stripped
        return v

class InvestmentResponse(InvestmentBase):
    id: str
    userId: str
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

class InvestmentDeleteResponse(BaseModel):
    message: str
    id: str
