from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class NotificationCreate(BaseModel):
    type: str = Field("info", min_length=1, max_length=64, description="Notification category/type")
    title: str = Field(..., min_length=1, max_length=255, description="Notification title")
    message: str = Field(..., min_length=1, max_length=1024, description="Notification message text")
    read: bool = Field(False, description="Read status flag")

class NotificationResponse(BaseModel):
    id: str
    userId: str
    type: str
    title: str
    message: str
    read: bool
    createdAt: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

class NotificationDeleteResponse(BaseModel):
    message: str
    id: str

class NotificationReadAllResponse(BaseModel):
    message: str
    count: int
