from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Literal


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