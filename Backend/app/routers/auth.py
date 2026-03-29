from fastapi import APIRouter, HTTPException, Response, status, Depends, Request
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schema import User
from app.config import settings
import uuid
from app.models import LoginRequest, RegisterRequest, AuthResponse
from app.dependencies import get_current_user
from supabase import create_client, Client
import os
from dotenv import load_dotenv


# load the .env file
load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["auth"])

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


def _set_auth_cookies(response: Response, session) -> None:
    """Helper to set the three auth cookies from a Supabase session object."""

    # set the access token cookie (httpOnly, secure, sameSite=None)
    response.set_cookie(
        key="sb-access-token",
        value=session.access_token,
        httponly=True,
        secure=False,   # Set True in production (HTTPS)
        samesite= os.getenv("SAMESITE", "none"),  # Use env var or default to 'none'
        max_age=session.expires_in,
    )

    # set the refresh token cookie (httpOnly, secure, sameSite=None)
    response.set_cookie(
        key="sb-refresh-token",
        value=session.refresh_token,
        httponly=True,
        secure=False,
        samesite= os.getenv("SAMESITE", "none"),  # Use env var or default to 'none'
        max_age=7 * 24 * 60 * 60,  # 7 days
    )

    # set a non-httpOnly cookie with the user ID for frontend use (optional, can be decoded from access token if needed)
    response.set_cookie(
        key="user-id",
        value="",       # cleared — no longer needed for auth
        httponly=False,
        secure=False,
        samesite= os.getenv("SAMESITE", "none"),  # Use env var or default to 'none'
        max_age=0,
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, response: Response, db: DBSession = Depends(get_db)):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password,
        })

        print("auth response is", auth_response)
        print("\n\n")

        if not auth_response.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        supabase_user = auth_response.user
        print("supabase user is", supabase_user)

        user = db.query(User).filter(User.supabase_user_id == uuid.UUID(supabase_user.id)).first()
        print("database user is", user)

        if not user:
            user = User(
                supabase_user_id=uuid.UUID(supabase_user.id),
                email=supabase_user.email,
                full_name=supabase_user.user_metadata.get("full_name", req.email.split("@")[0]),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # set all the cookies from the Supabase session
        _set_auth_cookies(response, auth_response.session)

        return AuthResponse(
            success=True,
            message="Login successful",
            user={"id": str(user.id), "email": user.email, "name": user.full_name},
            session={
                "access_token": auth_response.session.access_token,
                "expires_at": auth_response.session.expires_at,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed: {str(e)}")


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, response: Response, db: DBSession = Depends(get_db)):
    try:
        auth_response = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password,
            "options": {"data": {"full_name": req.name}},
        })

        if not auth_response.user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed. Email may already be in use.")

        supabase_user = auth_response.user

        user = User(
            supabase_user_id=uuid.UUID(supabase_user.id),
            email=req.email,
            full_name=req.name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        if auth_response.session:
            _set_auth_cookies(response, auth_response.session)

        return AuthResponse(
            success=True,
            message="Registration successful" if auth_response.session else "Registration successful. Please check your email for verification.",
            user={"id": str(user.id), "email": user.email, "name": user.full_name},
            session={
                "access_token": auth_response.session.access_token if auth_response.session else None,
                "expires_at": auth_response.session.expires_at if auth_response.session else None,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(e)}")


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    """Use the refresh token cookie to get a new access token."""
    refresh_token_value = request.cookies.get("sb-refresh-token")
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    try:
        result = supabase.auth.refresh_session(refresh_token_value)
        if not result or not result.session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token refresh failed")

        _set_auth_cookies(response, result.session)
        return {"success": True, "message": "Token refreshed"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token refresh failed: {str(e)}")


@router.post("/logout")
async def logout(response: Response):
    """Sign out and clear all auth cookies."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    for cookie in ("sb-access-token", "sb-refresh-token", "user-id"):
        response.delete_cookie(key=cookie, samesite="none", secure=False)

    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user, validated via Supabase JWT."""
    return {
        "success": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.full_name,
        },
    }
