from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str


class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.ANALYST


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None 