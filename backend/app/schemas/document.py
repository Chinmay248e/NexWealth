from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


DOCUMENT_TYPES = [
    "Tax Return",
    "Insurance",
    "Investment",
    "Invoice",
    "Salary Slip",
    "Other",
]


class DocumentBase(BaseModel):
    fileName: str = Field(..., min_length=1, max_length=255, description="Document filename")
    documentType: str = Field(..., min_length=1, max_length=64, description="Document category/type")
    status: str = Field(default="uploaded", max_length=32, description="Status (uploaded, verified, pending)")

    @field_validator("fileName")
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("File name cannot be blank.")
        return stripped

    @field_validator("documentType")
    @classmethod
    def validate_doc_type(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Document type cannot be blank.")
        return stripped


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    fileName: Optional[str] = Field(None, min_length=1, max_length=255)
    documentType: Optional[str] = Field(None, min_length=1, max_length=64)
    status: Optional[str] = Field(None, min_length=1, max_length=32)

    @field_validator("fileName")
    @classmethod
    def validate_file_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("File name cannot be blank.")
            return stripped
        return v


class DocumentResponse(DocumentBase):
    id: str
    userId: str
    uploadedAt: datetime
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class DocumentDeleteResponse(BaseModel):
    message: str
    id: str
