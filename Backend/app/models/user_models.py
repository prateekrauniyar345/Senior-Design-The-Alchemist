from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class User(BaseModel):
    """The full user model matching the database table exactly"""
    id: UUID
    supabase_user_id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    # Enables compatibility with SQLAlchemy (e.g., User.model_validate(db_user))
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    """Used for initial creation/sync from Supabase"""
    supabase_user_id: UUID
    email: EmailStr
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    """Requirement: Update ONLY the full_name"""
    full_name: str

class UserDelete(BaseModel):
    """Requirement: Delete ONLY by email"""
    email: EmailStr


class UserResponse(BaseModel):
    """
    Returns every field of the User class. 
    Using a separate class allows you to add API-only fields later 
    without changing your core Database model.
    """
    id: UUID
    supabase_user_id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)