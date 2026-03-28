from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    supabase_user_id: UUID


class UserCreate(UserBase):
    """Used for creating a new user (usually via Supabase webhook or signup)"""
    pass


class UserUpdate(BaseModel):
    """Used for patching user data"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class User(UserBase):
    """The full user model returned to the client"""
    id: UUID
    created_at: datetime

    # This allows Pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class UserWithRelations(User):
    """
    Optional: Use this if you want to nest related data 
    (Requires corresponding Pydantic models for Session, Message, etc.)
    """
    # sessions: List[Session] = []
    # messages: List[Message] = []
    pass