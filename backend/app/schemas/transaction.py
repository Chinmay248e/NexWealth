from datetime import datetime, date as date_type
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TransactionBase(BaseModel):
    type: str = Field(..., pattern="^(income|expense)$", description="Transaction type ('income' or 'expense')")
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=14)
    category: str = Field(..., min_length=1, max_length=64)
    date: date_type = Field(default_factory=date_type.today)
    source: str = Field(..., min_length=1, max_length=255)

class TransactionResponse(TransactionBase):
    id: str
    userId: str
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
