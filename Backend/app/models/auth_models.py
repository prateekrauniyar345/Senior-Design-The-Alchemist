# Backend/app/models/auth_models.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Literal
from uuid import UUID
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    session: Optional[dict] = None


class CurrentUserResponse(BaseModel):
    """Response model for /me endpoint"""
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True