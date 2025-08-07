from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.schemas.auth import UserResponse


class ActivityBase(BaseModel):
    activity_type: str
    title: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    activity_metadata: Optional[Dict[str, Any]] = None


class ActivityCreate(ActivityBase):
    user_id: int


class ActivityResponse(ActivityBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class ActivityList(BaseModel):
    activities: list[ActivityResponse]
    total: int 