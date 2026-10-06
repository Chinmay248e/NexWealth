from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full name of user")
    email: EmailStr = Field(..., description="Unique user email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="User password (will be securely hashed)")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Account password")

class UserResponse(UserBase):
    id: str
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

class TokenResponse(BaseModel):
    accessToken: str = Field(..., alias="access_token")
    tokenType: str = Field("bearer", alias="token_type")
    user: UserResponse

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
