from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["auth"])


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


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, response: Response):
    """
    Login endpoint - currently a stub for testing.
    TODO: Implement actual authentication with database lookup and password verification.
    """
    # TEMPORARY: Accept any credentials for testing
    # In production, you should:
    # 1. Look up user in database by email
    # 2. Verify password hash
    # 3. Create session/JWT token
    # 4. Set httpOnly cookie
    
    # For now, just set a dummy cookie and return success
    response.set_cookie(
        key="session",
        value=f"user_{req.email}",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return AuthResponse(
        success=True,
        message="Login successful",
        user={
            "email": req.email,
            "name": "Test User"
        }
    )


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, response: Response):
    """
    Registration endpoint - currently a stub for testing.
    TODO: Implement actual user creation in database.
    """
    # TEMPORARY: Accept any registration for testing
    # In production, you should:
    # 1. Check if email already exists
    # 2. Hash password (use bcrypt/argon2)
    # 3. Create user in database
    # 4. Create session/JWT token
    # 5. Set httpOnly cookie
    
    # For now, just set a dummy cookie and return success
    response.set_cookie(
        key="session",
        value=f"user_{req.email}",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return AuthResponse(
        success=True,
        message="Registration successful",
        user={
            "email": req.email,
            "name": req.name
        }
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout endpoint - clears session cookie."""
    response.delete_cookie(key="session")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user():
    """
    Get current authenticated user.
    TODO: Implement actual session/JWT validation.
    """
    # TEMPORARY: Return dummy user
    return {
        "email": "test@example.com",
        "name": "Test User"
    }
