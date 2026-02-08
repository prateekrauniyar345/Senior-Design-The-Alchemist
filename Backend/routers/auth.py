from fastapi import APIRouter, HTTPException, Response, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from Backend.database import get_db
from Backend.schema import User
from Backend.config import settings
import uuid
from Backend.models import LoginRequest, RegisterRequest, AuthResponse
from supabase import create_client, Client

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Initialize Supabase client
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)



@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, response: Response, db: DBSession = Depends(get_db)):
    """
    Login endpoint - uses Supabase auth and syncs with local database.
    """
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        supabase_user = auth_response.user
        
        # Check if user exists in local database, create if not
        user = db.query(User).filter(User.supabase_user_id == uuid.UUID(supabase_user.id)).first()
        
        if not user:
            # Create user in local database
            user = User(
                supabase_user_id=uuid.UUID(supabase_user.id),
                email=supabase_user.email,
                full_name=supabase_user.user_metadata.get("full_name", req.email.split("@")[0])
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Set session cookie with access token
        response.set_cookie(
            key="sb-access-token",
            value=auth_response.session.access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=auth_response.session.expires_in
        )
        
        response.set_cookie(
            key="sb-refresh-token",
            value=auth_response.session.refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user={
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name
            },
            session={
                "access_token": auth_response.session.access_token,
                "expires_at": auth_response.session.expires_at
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, response: Response, db: DBSession = Depends(get_db)):
    """
    Registration endpoint - creates user in Supabase and local database.
    """
    try:
        # Register with Supabase
        auth_response = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password,
            "options": {
                "data": {
                    "full_name": req.name
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Email may already be in use."
            )
        
        supabase_user = auth_response.user
        
        # Create user in local database
        user = User(
            supabase_user_id=uuid.UUID(supabase_user.id),
            email=req.email,
            full_name=req.name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Set session cookies if session exists
        if auth_response.session:
            response.set_cookie(
                key="sb-access-token",
                value=auth_response.session.access_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=auth_response.session.expires_in
            )
            
            response.set_cookie(
                key="sb-refresh-token",
                value=auth_response.session.refresh_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=7 * 24 * 60 * 60
            )
        
        return AuthResponse(
            success=True,
            message="Registration successful. Please check your email for verification." if not auth_response.session else "Registration successful",
            user={
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name
            },
            session={
                "access_token": auth_response.session.access_token if auth_response.session else None,
                "expires_at": auth_response.session.expires_at if auth_response.session else None
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/logout")
async def logout(response: Response):
    """Logout endpoint - clears session cookies and signs out from Supabase."""
    try:
        supabase.auth.sign_out()
    except:
        pass
    
    response.delete_cookie(key="sb-access-token")
    response.delete_cookie(key="sb-refresh-token")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(db: DBSession = Depends(get_db)):
    """
    Get current authenticated user from session.
    This is a simplified version - in production, validate the token from cookies.
    """
    # For now, return None - proper implementation would:
    # 1. Get access token from cookies
    # 2. Verify token with Supabase
    # 3. Look up user in local database
    # 4. Return user info
    
    # TODO: Implement proper token validation
    return {"user": None}
