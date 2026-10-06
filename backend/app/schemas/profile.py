from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Full name of user")
    email: Optional[EmailStr] = Field(None, description="User email address")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Name cannot be blank.")
            return stripped
        return v

class ProfileResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
