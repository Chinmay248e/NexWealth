from datetime import datetime, date as date_type
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class IncomeBase(BaseModel):
    source: str = Field(..., min_length=1, max_length=255, description="Income source / narration")
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        max_digits=14,
        description="Monetary amount in INR (must be positive Decimal)",
    )
    date: date_type = Field(default_factory=date_type.today, description="Date income was received (YYYY-MM-DD)")

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Income source cannot be blank.")
        return stripped

class IncomeCreate(IncomeBase):
    pass

class IncomeUpdate(BaseModel):
    source: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, max_digits=14)
    date: Optional[date_type] = None

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Income source cannot be blank.")
            return stripped
        return v

class IncomeResponse(IncomeBase):
    id: str
    userId: str
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

class IncomeDeleteResponse(BaseModel):
    message: str
    id: str
