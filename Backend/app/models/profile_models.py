from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class Profile(BaseModel):
    """The full profile model matching the Supabase 'profiles' table exactly"""
    id: UUID
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None 
    avatar_url: Optional[str] = None
    bio: Optional[str] = None  # Added to match table
    preferences: Optional[Dict[str, Any]] = None # Renamed from profile_data
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ProfileResponse(BaseModel):
    """Returns every field of the Profile class to the client"""
    id: UUID
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ProfileCreate(BaseModel):
    """Used for initial creation of a profile"""
    id: UUID 
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class ProfileUpdate(BaseModel):
    """Update profile fields (excluding email)"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class ProfileDelete(BaseModel):
    """Delete profile by email"""
    email: EmailStr