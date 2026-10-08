from datetime import datetime, date as date_type
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class BankStatementBase(BaseModel):
    fileName: str = Field(..., min_length=1, max_length=255, description="Statement file name")
    accountName: str = Field(..., min_length=1, max_length=255, description="Account name / Bank name")
    status: str = Field(default="uploaded", max_length=32, description="Status (uploaded, processing, parsed, failed)")

    @field_validator("fileName")
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("File name cannot be blank.")
        return stripped

    @field_validator("accountName")
    @classmethod
    def validate_account_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Account name cannot be blank.")
        return stripped


class BankStatementCreate(BankStatementBase):
    pass


class BankStatementUpdate(BaseModel):
    fileName: Optional[str] = Field(None, min_length=1, max_length=255)
    accountName: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, min_length=1, max_length=32)


class BankStatementResponse(BankStatementBase):
    id: str
    userId: str
    uploadedAt: datetime
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class BankStatementDeleteResponse(BaseModel):
    message: str
    id: str


class ParsedTransactionItem(BaseModel):
    date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    description: str = Field(..., min_length=1, description="Narration / Description")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Amount in INR")
    type: str = Field(..., description="'income' or 'expense'")
    category: str = Field(default="Other", description="Assigned category")
    source: str = Field(default="Bank Statement", description="Payment source / bank account")


class BankStatementParseResult(BaseModel):
    statementId: str
    fileName: str
    accountName: str
    status: str
    transactionCount: int
    totalCredits: Decimal
    totalDebits: Decimal
    transactions: List[ParsedTransactionItem]


class ImportTransactionsRequest(BaseModel):
    transactions: List[ParsedTransactionItem]


class ImportTransactionsResponse(BaseModel):
    message: str
    importedCount: int
    statementId: str
